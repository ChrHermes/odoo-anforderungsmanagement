// Real Odoo-18 UI checks, including a separate user denied Helpdesk access.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const {chromium} = await import(pathToFileURL(path.join(root, '.local/browser/node_modules/playwright/index.mjs')));
const local = path.join(root, '.local/dev');
const credentials = JSON.parse(await fs.readFile(path.join(local, 'credentials.json')));
const output = path.join(local, 'browser-ux');
await fs.mkdir(output, {recursive: true});
const expectedStates = ['new', 'review', 'evaluated', 'planned', 'in_progress', 'implemented', 'deferred', 'rejected'];
const expectedColors = {'GridCal Node': '#0068b1', 'GridCal Operator': '#40d0d7', 'GridCal Core': '#4a0a7c', 'GridCal Nexus': '#c51a82', 'GridCal Allgemeines': '#fa4d0f'};
const browser = await chromium.launch({headless: true});
const errors = [];
const completed = [];
async function newPage(restricted = false) {
    const context = await browser.newContext({viewport: {width: 1560, height: 1000}});
    await context.route('**/*', route => {
        const url = new URL(route.request().url());
        if (url.hostname === 'localhost' && url.port === '8069') return route.continue();
        errors.push('External request: ' + url.origin);
        return route.abort();
    });
    const page = await context.newPage();
    page.setDefaultTimeout(20000);
    page.on('pageerror', error => errors.push(error.message));
    await page.goto('http://localhost:8069/local-dev');
    const prefix = restricted ? 'restricted_' : '';
    await page.locator('#login').fill(credentials[prefix + 'login']);
    await page.locator('#password').fill(credentials[prefix + 'password']);
    await page.locator('button[type=submit]').click();
    await page.locator('a.card').first().click();
    await page.locator('.o_kanban_group').first().waitFor();
    return page;
}
async function rpc(page, model, method, args = [], kwargs = {}, denied = false) {
    const result = await page.evaluate(async ({model, method, args, kwargs}) => {
        const response = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({jsonrpc: '2.0', method: 'call', params: {model, method, args, kwargs}}),
        });
        return response.json();
    }, {model, method, args, kwargs});
    if (denied) {
        assert.ok(result.error, method + ' must deny raw snapshot access');
        return;
    }
    assert.ok(!result.error, JSON.stringify(result.error));
    return result.result;
}
async function pass(name) { completed.push(name); console.log('PASS:', name); }
let page;
let productToRestore;
try {
    page = await newPage();
    const states = await page.locator('.o_kanban_group').evaluateAll(nodes => nodes.map(node => node.dataset.gcState));
    assert.deepEqual(states, expectedStates);
    const products = await rpc(page, 'gc.requirement.product', 'search_read', [], {domain: [], fields: ['name', 'color_hex']});
    for (const [name, color] of Object.entries(expectedColors)) {
        const product = products.find(row => row.name === name);
        assert.ok(product, name);
        assert.equal(product.color_hex, color);
    }
    for (const type of ['feature', 'improvement', 'bug']) assert.ok(await page.locator('.gc_requirement_type_' + type).count());
    const badges = await page.locator('.gc_product_badge').evaluateAll(nodes => nodes.map(node => ({name: node.textContent.trim(), bg: getComputedStyle(node).backgroundColor, fg: getComputedStyle(node).color})));
    assert.equal(badges.find(row => row.name === 'GridCal Node').fg, 'rgb(255, 255, 255)');
    assert.equal(badges.find(row => row.name === 'GridCal Operator').fg, 'rgb(33, 37, 41)');
    const paths = await page.locator('.gc_category_path').allTextContents();
    assert.ok(paths.every(value => !value.startsWith('GridCal ')));
    assert.match(await page.locator('.gc_category_path').first().getAttribute('title'), /^GridCal /);
    await page.screenshot({path: path.join(output, 'kanban.png'), fullPage: true});
    await page.locator('.o_kanban_group[data-gc-state="deferred"]').scrollIntoViewIfNeeded();
    const deferredStyle = await page.locator('[data-gc-state="deferred"]').evaluate(node => ({margin: getComputedStyle(node).marginLeft, border: getComputedStyle(node).borderLeftWidth}));
    assert.equal(deferredStyle.margin, '12px');
    assert.equal(deferredStyle.border, '1px');
    await page.screenshot({path: path.join(output, 'kanban-terminal.png'), fullPage: true});
    // Empty filtered results retain all eight columns.
    const search = page.locator('.o_searchview_input');
    await search.fill('UX-no-record-match-20261022');
    await search.press('Enter');
    await page.locator('.o_searchview_facet').first().waitFor();
    await page.waitForFunction(() => document.querySelectorAll('.o_kanban_record:not(.o_kanban_ghost)').length === 0);
    assert.deepEqual(await page.locator('.o_kanban_group').evaluateAll(nodes => nodes.map(node => node.dataset.gcState)), expectedStates);
    await page.screenshot({path: path.join(output, 'kanban-empty.png'), fullPage: true});
    await page.goto('http://localhost:8069/local-dev');
    await page.locator('a.card').first().click();
    await page.locator('.gc_product_badge').first().waitFor();
    await page.setViewportSize({width: 720, height: 950});
    await page.screenshot({path: path.join(output, 'kanban-narrow.png'), fullPage: true});
    await page.setViewportSize({width: 1560, height: 1000});
    await pass('Ordered/empty/narrow Kanban, all five exact colors, contrast, type tags and relative category paths');

    await page.getByRole('button', {name: 'Konfiguration', exact: true}).click();
    await page.getByRole('menuitem', {name: 'Produkte', exact: true}).click();
    await page.locator('.o_data_row').first().waitFor();
    await page.screenshot({path: path.join(output, 'product-list.png'), fullPage: true});
    await page.getByText('GridCal Node', {exact: true}).click();
    const colorInput = page.getByPlaceholder('#0068b1');
    await colorInput.waitFor();
    productToRestore = products.find(row => row.name === 'GridCal Node');
    await colorInput.fill('#123456');
    await page.locator('.o_form_button_save').click();
    await page.locator('.o_form_button_save').waitFor({state: 'hidden'});
    assert.equal((await rpc(page, 'gc.requirement.product', 'read', [[productToRestore.id], ['color_hex']]))[0].color_hex, '#123456');
    await colorInput.fill(productToRestore.color_hex);
    await page.locator('.o_form_button_save').click();
    await page.locator('.o_form_button_save').waitFor({state: 'hidden'});
    await page.screenshot({path: path.join(output, 'product-configuration.png'), fullPage: true});
    productToRestore = undefined;
    await pass('Native product configuration: hex edit, persistence, picker preview and restoration');

    const requirements = await rpc(page, 'gc.requirement', 'search_read', [], {domain: [], fields: ['reference', 'ticket_count']});
    const linked = requirements.find(row => row.ticket_count > 0);
    const empty = requirements.find(row => row.ticket_count === 0);
    const sources = await rpc(page, 'gc.requirement', 'get_authorized_sources', [[linked.id]]);
    assert.ok(sources.length && sources[0].description_snapshot);
    await page.goto(`http://localhost:8069/odoo/gc.requirement/${linked.id}`);
    await page.getByRole('tab', {name: 'Kunden & Tickets', exact: true}).click();
    await page.getByRole('button', {name: 'Ursprüngliche Ticketbeschreibungen anzeigen', exact: true}).click();
    await page.locator('.modal').waitFor();
    assert.match(await page.locator('.modal').innerText(), /Synthetische Originalbeschreibung/);
    await page.screenshot({path: path.join(output, 'authorized-snapshot.png'), fullPage: true});
    await page.goto(`http://localhost:8069/odoo/gc.requirement/${empty.id}`);
    await page.getByRole('tab', {name: 'Kunden & Tickets', exact: true}).click();
    await page.getByText('Keine Helpdesk-Tickets verknüpft.', {exact: true}).waitFor();
    await page.screenshot({path: path.join(output, 'no-tickets.png'), fullPage: true});
    await pass('Authorized original snapshot and explicit no-ticket empty state');

    const deniedPage = await newPage(true);
    assert.equal(await deniedPage.getByRole('button', {name: 'Konfiguration', exact: true}).count(), 0);
    assert.deepEqual(await rpc(deniedPage, 'gc.requirement', 'get_authorized_sources', [[linked.id]]), []);
    const publicRows = await rpc(deniedPage, 'gc.requirement', 'read', [[linked.id]]);
    assert.ok(!JSON.stringify(publicRows).includes('Synthetische Originalbeschreibung'));
    const raw = 'gc.requirement.ticket.source';
    for (const [method, args] of [
        ['read', [[1], ['description_snapshot']]],
        ['search_read', [[], ['description_snapshot']]],
        ['read_group', [[], ['description_snapshot:count'], []]],
        ['export_data', [[1], ['description_snapshot']]],
        ['search_count', [[]]],
    ]) await rpc(deniedPage, raw, method, args, {}, true);
    await deniedPage.goto(`http://localhost:8069/odoo/gc.requirement/${linked.id}`);
    await deniedPage.getByRole('tab', {name: 'Kunden & Tickets', exact: true}).click();
    await deniedPage.getByRole('button', {name: 'Ursprüngliche Ticketbeschreibungen anzeigen', exact: true}).click();
    await deniedPage.getByText(/Keine zugänglichen Ticketquellen/).waitFor();
    assert.ok(!(await deniedPage.locator('.modal').innerText()).includes('Synthetische Originalbeschreibung'));
    await deniedPage.screenshot({path: path.join(output, 'denied-snapshot.png'), fullPage: true});
    await pass('Separate internal user: UI/adapter/read/search/group/export/count deny ticket snapshots');
    assert.deepEqual(errors, []);
    await fs.writeFile(path.join(output, 'result.json'), JSON.stringify({completed, states, badges, errors, time: new Date().toISOString(), enterpriseAcceptance: false}, null, 2));
    console.log('PASS: local Odoo-18 UX browser checks; screenshots:', output);
} catch (error) {
    if (page) {
        await page.screenshot({path: path.join(output, 'failure.png'), fullPage: true});
        await fs.writeFile(path.join(output, 'failure.txt'), await page.locator('body').innerText());
    }
    throw error;
} finally {
    if (productToRestore && page) await rpc(page, 'gc.requirement.product', 'write', [[productToRestore.id], {color_hex: productToRestore.color_hex}]);
    await browser.close();
}
