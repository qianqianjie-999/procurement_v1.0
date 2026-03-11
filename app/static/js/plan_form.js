/**
 * 采购计划表单 JavaScript（匹配 Excel 模板）
 *
 * 功能：
 * 1. 动态添加/删除物资明细行
 * 2. 行号自动更新
 * 3. 表单提交前验证
 */

(function() {
    'use strict';

    // DOM 元素 - 可能在某些页面上不存在
    const itemsBody = document.getElementById('itemsBody');
    const addRowBtn = document.getElementById('addRowBtn');
    const rowTemplate = document.getElementById('rowTemplate');
    const hiddenFields = document.getElementById('hiddenFields');
    const planForm = document.getElementById('planForm');

    // 如果不是采购计划表单页面，直接返回
    if (!itemsBody || !addRowBtn || !rowTemplate || !planForm) {
        return;
    }

    // 行计数器
    let rowCount = 0;

    /**
     * 添加新行
     * @param {Object} data - 可选的初始数据
     */
    function addRow(data = null) {
        const clone = rowTemplate.content.cloneNode(true);
        const row = clone.querySelector('.item-row');

        // 设置行号
        rowCount++;
        row.querySelector('.row-number').textContent = rowCount;

        // 如果有初始数据，填充到行中
        if (data) {
            // 填充物资名称
            if (data.item_name) {
                row.querySelector('.item-name').value = data.item_name;
            }
            // 填充 ID（编辑模式）
            if (data.id) {
                row.querySelector('.item-id').value = data.id;
            }
            // 填充品牌型号
            if (data.brand_model) {
                row.querySelector('input[name="brand_models[]"]').value = data.brand_model;
            }
            // 填充主要规格
            if (data.specification) {
                row.querySelector('input[name="specifications[]"]').value = data.specification;
            }
            // 填充数量
            if (data.quantity) {
                row.querySelector('.quantity').value = parseFloat(data.quantity).toFixed(4);
            }
            // 填充单位
            if (data.unit) {
                row.querySelector('input[name="units[]"]').value = data.unit;
            }
            // 填充批次数量
            if (data.batch_quantity) {
                row.querySelector('input[name="batch_quantities[]"]').value = parseFloat(data.batch_quantity).toFixed(4);
            }
            // 填充合同外数量
            if (data.extra_contract_quantity) {
                row.querySelector('input[name="extra_contract_quantities[]"]').value = parseFloat(data.extra_contract_quantity).toFixed(4);
            }
            // 填充计划到货时间
            if (data.required_date) {
                row.querySelector('input[name="required_dates[]"]').value = data.required_date;
            }
            // 填充备注
            if (data.remarks) {
                row.querySelector('input[name="remarks[]"]').value = data.remarks;
            }
        }

        // 绑定事件
        bindRowEvents(row);

        // 添加到表格
        itemsBody.appendChild(row);
    }

    /**
     * 删除行
     * @param {HTMLElement} row - 要删除的行
     */
    function deleteRow(row) {
        // 确保至少保留一行
        if (itemsBody.querySelectorAll('.item-row').length <= 1) {
            showToast('请至少保留一行物资明细', 'warning');
            return;
        }

        // 删除行
        row.remove();

        // 重新编号
        renumberRows();
    }

    /**
     * 重新编号所有行
     */
    function renumberRows() {
        rowCount = 0;
        itemsBody.querySelectorAll('.item-row').forEach(row => {
            rowCount++;
            row.querySelector('.row-number').textContent = rowCount;
        });
    }

    /**
     * 绑定行事件
     * @param {HTMLElement} row - 行元素
     */
    function bindRowEvents(row) {
        // 删除按钮
        const deleteBtn = row.querySelector('.delete-row');
        deleteBtn.addEventListener('click', function() {
            if (confirm('确定要删除此行吗？')) {
                deleteRow(row);
            }
        });

        // 数量变化时验证
        const quantityInput = row.querySelector('.quantity');
        quantityInput.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(4);
            }
        });
    }

    /**
     * 显示提示消息
     * @param {string} message - 消息内容
     * @param {string} type - 消息类型 (success, danger, warning, info)
     */
    function showToast(message, type = 'info') {
        // 创建 toast 元素
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(toast);

        // 5 秒后自动移除
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    /**
     * 表单提交前验证
     * @param {Event} e - 提交事件
     */
    function validateForm(e) {
        // 检查是否有空行
        const rows = itemsBody.querySelectorAll('.item-row');
        let hasValidItem = false;
        let hasInvalidRow = false;

        rows.forEach(row => {
            const itemName = row.querySelector('.item-name').value.trim();
            const quantity = row.querySelector('.quantity').value;

            if (itemName && quantity) {
                // 有效的物资明细
                hasValidItem = true;
            } else if (itemName && !quantity) {
                // 有名称没有数量 - 无效
                hasInvalidRow = true;
            } else if (!itemName && quantity) {
                // 有数量没有名称 - 无效
                hasInvalidRow = true;
            }
            // 如果都为空，则是空行，会被移除
        });

        // 移除空行
        rows.forEach(row => {
            const itemName = row.querySelector('.item-name').value.trim();
            const quantity = row.querySelector('.quantity').value;

            if (!itemName && !quantity) {
                row.remove();
            }
        });

        renumberRows();

        // 验证有无效的 row
        if (hasInvalidRow) {
            e.preventDefault();
            showToast('请填写完整的物资明细（名称和数量必填）', 'danger');
            return false;
        }

        // 验证至少有一行数据
        if (!hasValidItem) {
            e.preventDefault();
            showToast('请至少添加一项物资明细', 'warning');
            return false;
        }

        return true;
    }

    /**
     * 初始化表单
     */
    function initForm() {
        // 绑定添加按钮事件
        addRowBtn.addEventListener('click', function() {
            addRow();
        });

        // 绑定表单提交验证
        planForm.addEventListener('submit', validateForm);

        // 加载初始数据
        if (initialItems && initialItems.length > 0) {
            initialItems.forEach(function(item) {
                addRow(item);
            });
        } else {
            // 添加一行空行
            addRow();
        }
    }

    // DOM 加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initForm);
    } else {
        initForm();
    }
})();
