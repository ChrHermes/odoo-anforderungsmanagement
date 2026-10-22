// Local-only real-browser smoke check. Install Playwright into .local/browser first.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const {chromium} = await import(pathToFileURL(path.join(root, '.local/browser/node_modules/playwright/index.mjs')));
const local = path.join(root, '.local/dev');
const credentials = JSON.parse(await fs.readFile(path.join(local, 'credentials.json')));
const settings = JSON.parse(await fs.readFile(path.join(local, 'settings.json')));
assert.equal(settings.database, 'gc_requirements_dev');
const output = path.join(local, 'browser-planning');
await fs.mkdir(output, {recursive: true});
await Promise.all(['failure.txt', 'failure.png', 'result.json'].map(name => fs.rm(path.join(output, name), {force: true})));
const browser = await chromium.launch({headless: true});
const context = await browser.newContext({viewport: {width: 1440, height: 1000}});
const page = await context.newPage();
page.setDefaultTimeout(20000);
const errors = [];
const external = [];
const completed = [];
page.on('pageerror', error => errors.push(error.message));
await context.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.protocol === 'data:' || (url.hostname === 'localhost' && url.port === '8069')) {
        return route.continue();
    }
    external.push(url.origin);
    return route.abort();
});
async function step(name, callback) {
    await callback();
    completed.push(name);
    console.log('PASS:', name);
}
async function rpc(model, method, args = [], kwargs = {}) {
    return page.evaluate(async ({model, method, args, kwargs}) => {
        const response = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({jsonrpc: '2.0', method: 'call', params: {model, method, args, kwargs}}),
        });
        const data = await response.json();
        if (data.error) throw new Error(JSON.stringify(data.error));
        return data.result;
    }, {model, method, args, kwargs});
}
async function record(title) {
    const rows = await rpc('gc.requirement', 'search_read', [], {
        domain: [['name', '=', title]], fields: ['name', 'reference', 'state', 'priority', 'product_id', 'category_id', 'activity_ids'],
    });
    assert.equal(rows.length, 1);
    return rows[0];
}
async function selectRelation(field, text, option) {
    await page.locator(`.o_field_widget[name="${field}"] input`).fill(text);
    await page.locator('.o-autocomplete--dropdown-menu').getByText(option, {exact: true}).click();
}

let planId;
const title = `Release Browserprüfung ${new Date().toISOString()}`;
try {
    await step('Anmeldung, Releaseplanung und Produktfarben', async () => {
        await page.goto('http://localhost:8069/local-dev');
        await page.locator('#login').fill(credentials.login);
        await page.locator('#password').fill(credentials.password);
        await page.locator('button[type=submit]').click();
        await page.locator('a.card').first().click();
        await page.locator('.o_kanban_record').first().waitFor();
        await page.getByText('Releaseplanung', {exact: true}).first().click();
        await page.locator('.o_kanban_record').first().waitFor();
        await page.getByText('SCADA-Ausbau Q2 2027', {exact: true}).waitFor();
        assert.ok(await page.locator('.gc_product_badge').count() >= 4);
        await page.screenshot({path: path.join(output, 'planning-kanban.png'), fullPage: true});
        await page.locator('.o_switch_view.o_list').click();
        await page.locator('.o_data_row').first().waitFor();
        await page.screenshot({path: path.join(output, 'planning-list.png'), fullPage: true});
    });
    await step('Release im nativen Formular anlegen und bestehende Anforderung auswählen', async () => {
        await page.getByRole('button', {name: 'Neu', exact: true}).click();
        await page.locator('.o_field_widget[name="name"] input').fill(title);
        await selectRelation('product_id', 'GridCal Node', 'GridCal Node');
        await page.locator('.o_field_widget[name="version"] input').fill('TARGET-2027.2');
        await page.locator('.o_form_button_save').click();
        await page.locator('.o_form_button_save').waitFor({state: 'hidden'});
        const plans = await rpc('gc.requirement.milestone', 'search_read', [], {domain: [['name', '=', title]], fields: ['reference']});
        assert.equal(plans.length, 1);
        planId = plans[0].id;
        assert.match(plans[0].reference, /^MS-\d+$/);
        const req = await rpc('gc.requirement', 'create', [{name: title + ' Requirement', description: '<p>Browser planning test</p>', request_type: 'feature', product_id: (await rpc('gc.requirement.product', 'search_read', [], {domain: [['name', '=', 'GridCal Node']], fields: ['name']}))[0].id}]);
        // Real native selection dialog, no relation RPC shortcut.
        await page.locator('.o_field_widget[name="assignment_ids"]').getByRole('button', {name: /Hinzufügen|Zeile hinzufügen/}).click();
        await page.locator('.modal .o_searchview_input').fill(title + ' Requirement');
        await page.locator('.modal .o_searchview_input').press('Enter');
        await page.locator('.modal .o_data_row').filter({hasText: title + ' Requirement'}).click();
        await page.locator('.modal').waitFor({state: 'hidden'});
        await page.locator('.o_form_button_save').click();
        await page.locator('.o_form_button_save').waitFor({state: 'hidden'});
        assert.equal((await rpc('gc.requirement', 'read', [[req], ['milestone_id']]))[0].milestone_id[0], planId);
        await page.screenshot({path: path.join(output, 'planning-detail.png'), fullPage: true});
    });
    await step('Abschlusswarnung, ausdrückliche Bestätigung und unveränderter Anforderungsstatus', async () => {
        await page.getByRole('button', {name: 'Veröffentlichen', exact: true}).click();
        await page.locator('.modal .alert-warning').waitFor();
        await page.screenshot({path: path.join(output, 'completion-warning.png'), fullPage: true});
        await page.locator('.modal .o_field_widget[name="confirmed"] input').check();
        await page.getByRole('button', {name: 'Abschluss übernehmen', exact: true}).click();
        await page.locator('.modal').waitFor({state: 'hidden'});
        const plan = (await rpc('gc.requirement.milestone', 'read', [[planId], ['state', 'open_count', 'completed_on']]))[0];
        assert.equal(plan.state, 'done');
        assert.equal(plan.open_count, 1);
        assert.ok(plan.completed_on);
        await page.screenshot({path: path.join(output, 'planning-published.png'), fullPage: true});
    });
    await step('Anforderungsnavigation, getrennte Planung und nativer GitLab-Link', async () => {
        await page.locator('button[name="action_view_requirements"]').click();
        await page.getByText(title + ' Requirement', {exact: true}).first().click();
        await page.getByRole('tab', {name: 'Weitere Informationen', exact: true}).click();
        await page.locator('.o_field_widget[name="worktimes_url"] input').fill('https://gitlab.example.invalid/worktimes/99');
        await page.locator('.o_field_widget[name="development_url"] input').fill('Independent development reference');
        await page.locator('.o_form_button_save').click();
        await page.locator('.o_form_button_save').waitFor({state: 'hidden'});
        const link = page.getByRole('link', {name: 'In GitLab öffnen', exact: true});
        assert.equal(await link.getAttribute('target'), '_blank');
        assert.equal(await link.getAttribute('href'), 'https://gitlab.example.invalid/worktimes/99');
        const rows = await rpc('gc.requirement', 'search_read', [], {domain: [['name', '=', title + ' Requirement']], fields: ['state', 'implemented_version', 'implemented_on', 'milestone_id', 'development_url', 'worktimes_url']});
        assert.equal(rows[0].state, 'new');
        assert.equal(rows[0].implemented_version, false);
        assert.equal(rows[0].implemented_on, false);
        assert.equal(rows[0].milestone_id[0], planId);
        assert.equal(rows[0].development_url, 'Independent development reference');
        await page.screenshot({path: path.join(output, 'requirement-planning-worktimes.png'), fullPage: true});
        await page.getByText('Ohne Planungszuordnung', {exact: true}).first().click();
        await page.locator('.o_list_view').waitFor();
        assert.equal(await page.getByText(title + ' Requirement', {exact: true}).count(), 0);
    });
    assert.deepEqual(errors, []);
    assert.deepEqual(external, []);
    await fs.writeFile(path.join(output, 'result.json'), JSON.stringify({completed, errors, external, planId, enterpriseAcceptance: false, time: new Date().toISOString()}, null, 2));
    console.log('PASS: local planning browser smoke; synthetic Helpdesk only. Screenshots:', output);
} catch (error) {
    await page.screenshot({path: path.join(output, 'failure.png'), fullPage: true});
    await fs.writeFile(path.join(output, 'failure.txt'), await page.locator('body').innerText());
    throw error;
} finally {
    await browser.close();
}
