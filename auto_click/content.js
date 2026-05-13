// ================= 安全启动检查 =================
let IS_ALIVE = true;

// 检查1: chrome 对象是否存在
if (typeof chrome === 'undefined' || !chrome.runtime || !chrome.storage) {
    IS_ALIVE = false;
}

// 检查2: 尝试获取插件ID，这是最有效的上下文检查
try {
    if (IS_ALIVE) {
        const temp = chrome.runtime.id; // 如果这行报错，直接进 catch
    }
} catch (e) {
    IS_ALIVE = false;
    console.log("⚠️ 插件上下文已失效，请刷新页面。");
}

// ================= 核心逻辑 (仅在安全时执行) =================
if (IS_ALIVE) {
    console.log("✅ 录制脚本已安全启动");

    // 1. 安全的选择器生成
    function getSafeSelector(el) {
        if (!el || el.nodeType !== 1) return null;
        
        try {
            if (el.id) return `#${el.id}`;
            
            if (el.classList && el.classList.length > 0) {
                return `${el.tagName.toLowerCase()}.${Array.from(el.classList).join('.')}`;
            }

            // 简单路径生成，避免过度遍历
            let path = [];
            let current = el;
            let count = 0;
            
            while (current && current !== document.body && count < 5) {
                if (!current.tagName) break;
                path.unshift(current.tagName.toLowerCase());
                current = current.parentElement;
                count++;
            }
            return path.join(' > ');
        } catch (e) {
            return null;
        }
    }

    // 2. 安全的存储操作
    function safeSave(action) {
        if (!IS_ALIVE) return;
        
        try {
            chrome.storage.local.get(['isRecording', 'actions'], (res) => {
                // 再次检查运行时错误
                if (chrome.runtime.lastError) {
                    IS_ALIVE = false;
                    return;
                }

                if (res.isRecording) {
                    const newActions = [...(res.actions || []), action];
                    chrome.storage.local.set({ actions: newActions }, () => {
                        if (chrome.runtime.lastError) IS_ALIVE = false;
                    });
                }
            });
        } catch (e) {
            IS_ALIVE = false;
        }
    }

    // 3. 事件监听 (带熔断机制)
    document.addEventListener('click', (e) => {
        if (!IS_ALIVE) return;
        const selector = getSafeSelector(e.target);
        if (selector) {
            safeSave({ type: 'click', selector: selector });
        }
    }, true);

    document.addEventListener('input', (e) => {
        if (!IS_ALIVE) return;
        if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
            const selector = getSafeSelector(e.target);
            if (selector) {
                safeSave({ type: 'input', selector: selector, value: e.target.value });
            }
        }
    }, true);
}