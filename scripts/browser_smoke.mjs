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
const output = path.join(local, 'browser');
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
let created;
const title = `Browserprüfung ${new Date().toISOString()}`;
const editedTitle = title + ' bearbeitet';
try {
    await step('Anmeldung und gekennzeichnete App-Kachel', async () => {
        await page.goto('http://localhost:8069/local-dev');
        await page.locator('#login').fill(credentials.login);
        await page.locator('#password').fill(credentials.password);
        await page.locator('button[type=submit]').click();
        await page.locator('a.card').first().waitFor();
        if (settings.mode === 'demo') assert.match(await page.locator('body').innerText(), /keine Enterprise-Abnahme/);
        await page.screenshot({path: path.join(output, 'launcher.png'), fullPage: true});
        await page.locator('a.card').first().click();
    });
    await step('Kanban, Statusgruppen und Listenansicht', async () => {
        await page.locator('.o_kanban_view .o_kanban_record').first().waitFor();
        assert.ok(await page.locator('.o_kanban_group').count() >= 8);
        await page.screenshot({path: path.join(output, 'kanban.png'), fullPage: true});
        await page.locator('.o_switch_view.o_list').click();
        await page.locator('.o_list_view .o_data_row').first().waitFor();
        assert.ok(await page.locator('.o_data_row').count() >= 8);
        await page.screenshot({path: path.join(output, 'list.png'), fullPage: true});
    });
    await step('Anlegen mit Redaktion, Produkt, Kategorie und drei Sternen', async () => {
        await page.getByRole('button', {name: 'Neu', exact: true}).click();
        await page.locator('.o_field_widget[name="name"] input').fill(title);
        await page.locator('.o_field_widget[name="request_type"] select').selectOption({label: 'Funktionswunsch'});
        await selectRelation('product_id', 'GridCal Node', 'GridCal Node');
        await selectRelation('category_id', 'Messgeräte', 'GridCal Node / BASE / Messgeräte');
        await page.locator('.odoo-editor-editable').fill('Redaktioneller Text aus einer echten lokalen Browserprüfung.');
        await page.locator('.o_field_widget[name="priority"] .o_priority_star').nth(2).click();
        await page.locator('.o_form_button_save').click();
        await page.locator('.o_form_button_save').waitFor({state: 'hidden'});
        created = await record(title);
        assert.match(created.reference, /^REQ-\d+$/);
        assert.equal(created.priority, '3');
        assert.match(created.category_id[1], /Messgeräte/);
    });
    await step('Bearbeiten und Statuswechsel über den Wizard', async () => {
        await page.locator('.o_field_widget[name="name"] input').fill(editedTitle);
        await page.locator('.o_form_button_save').click();
        await page.locator('.o_form_button_save').waitFor({state: 'hidden'});
        await page.getByRole('button', {name: 'Status ändern', exact: true}).click();
        await page.locator('.modal .o_field_widget[name="state"] select').selectOption({label: 'In Prüfung'});
        await page.getByRole('button', {name: 'Status übernehmen', exact: true}).click();
        await page.locator('.modal').waitFor({state: 'hidden'});
        assert.equal((await record(editedTitle)).state, 'review');
    });
    await step('Interne Chatternotiz', async () => {
        await page.getByRole('button', {name: 'Notiz hinterlassen', exact: true}).click();
        await page.locator('.o-mail-Composer-input').fill('Interne Notiz aus der Browserprüfung – nur synthetische Daten.');
        await page.getByRole('button', {name: 'Hinterlassen', exact: true}).click();
        await page.getByText('Interne Notiz aus der Browserprüfung – nur synthetische Daten.', {exact: true}).waitFor();
    });
    await step('Manuelle Aktivität', async () => {
        await page.getByRole('button', {name: 'Aktivitäten', exact: true}).click();
        await page.locator('.modal .o_field_widget[name="summary"] input').fill('Manuelle Browseraktivität');
        await page.getByRole('button', {name: 'Planen', exact: true}).click();
        await page.locator('.modal').waitFor({state: 'hidden'});
        assert.ok((await record(editedTitle)).activity_ids.length > 0);
        await page.screenshot({path: path.join(output, 'detail.png'), fullPage: true});
    });
    if (settings.mode === 'demo') {
        await step('Synthetisches Helpdesk: bestehende Anforderung über Ticketwizard verknüpfen', async () => {
            await page.goto('http://localhost:8069/local-dev');
            await page.getByRole('link', {name: /Helpdesk \(UI-Demo\)/}).click();
            await page.getByText('Demo-Ticket 3: Messwerte und Bedienung', {exact: true}).click();
            await page.locator('.o_cp_action_menus .dropdown-toggle').first().click();
            await page.getByRole('menuitem', {name: 'Anforderung erstellen/verknüpfen', exact: true}).click();
            await selectRelation('requirement_id', created.reference, `${created.reference} – ${editedTitle}`);
            await page.locator('.modal button[name="action_apply"]').click();
            await page.locator('.modal').waitFor({state: 'hidden'});
            const sources = await rpc('gc.requirement', 'get_authorized_sources', [[created.id]]);
            assert.equal(sources.length, 1);
            assert.match(sources[0].description_snapshot, /Synthetische Originalbeschreibung 3/);
            await page.getByRole('tab', {name: 'Kunden & Tickets', exact: true}).click();
            await page.getByRole('button', {name: 'Autorisierte Ticketquellen anzeigen', exact: true}).click();
            await page.getByText('Synthetische Originalbeschreibung 3. Keine Kundendaten.', {exact: true}).waitFor();
            await page.screenshot({path: path.join(output, 'source.png'), fullPage: true});
        });
    }
    assert.deepEqual(errors, [], 'Browser JavaScript errors');
    assert.deepEqual(external, [], 'Unexpected external browser requests');
    await fs.writeFile(path.join(output, 'result.json'), JSON.stringify({
        mode: settings.mode, completed, requirement: await record(editedTitle), errors, external,
        enterpriseAcceptance: false, time: new Date().toISOString(),
    }, null, 2));
    console.log('PASS: real browser smoke; no Enterprise acceptance. Screenshots:', output);
} catch (error) {
    await page.screenshot({path: path.join(output, 'failure.png'), fullPage: true});
    await fs.writeFile(path.join(output, 'failure.txt'), await page.locator('body').innerText());
    throw error;
} finally {
    await browser.close();
}
