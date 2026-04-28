/**
 * 食譜表單 — 動態新增食材與步驟欄位（Bootstrap 5 版）
 * 供 recipes/new.html 與 recipes/edit.html 使用
 */

function addIngredientRow() {
    const section = document.getElementById('ingredients-section');
    const row = document.createElement('div');
    row.className = 'ingredient-row row g-2 mb-2 align-items-end';
    row.innerHTML = `
        <div class="col-md-3">
            <input type="text" class="form-control form-control-sm" name="ingredient_name[]" placeholder="食材名稱" required>
        </div>
        <div class="col-md-2">
            <input type="number" class="form-control form-control-sm" name="ingredient_quantity[]" placeholder="數量" step="0.1" required>
        </div>
        <div class="col-md-2">
            <input type="text" class="form-control form-control-sm" name="ingredient_unit[]" placeholder="單位" required>
        </div>
        <div class="col-md-3">
            <input type="text" class="form-control form-control-sm" name="ingredient_notes[]" placeholder="備註">
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.closest('.ingredient-row').remove()">✕</button>
        </div>
    `;
    section.appendChild(row);
}

function addStepRow() {
    const section = document.getElementById('steps-section');
    const stepCount = section.querySelectorAll('.step-row').length + 1;
    const row = document.createElement('div');
    row.className = 'step-row row g-2 mb-2 align-items-start';
    row.innerHTML = `
        <div class="col-md-1 pt-2 text-center fw-bold">${stepCount}.</div>
        <div class="col-md-7">
            <textarea class="form-control form-control-sm" name="step_instruction[]" rows="2" placeholder="步驟說明" required></textarea>
        </div>
        <div class="col-md-2">
            <input type="number" class="form-control form-control-sm" name="step_timer[]" placeholder="計時（秒）" min="0">
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.closest('.step-row').remove()">✕</button>
        </div>
    `;
    section.appendChild(row);
}
