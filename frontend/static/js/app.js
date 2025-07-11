// HTMX 版本的应用程序逻辑
class HTMXApp {
    constructor() {
        this.initializeApp();
        this.setupEventListeners();
        this.setupHTMXEvents();
    }

    initializeApp() {
        this.elements = {
            messageInput: document.getElementById('message-input'),
            charCount: document.getElementById('char-count'),
            chatMessages: document.getElementById('chat-messages'),
            status: document.getElementById('status'),
            connectionStatus: document.getElementById('connection-status')
        };

        this.updateCharCount();
        this.updateStatus('就绪', 'success');
    }

    setupEventListeners() {
        // 字符计数
        if (this.elements.messageInput) {
            this.elements.messageInput.addEventListener('input', () => {
                this.updateCharCount();
            });
        }

        // 复制功能
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('copy-button')) {
                this.copyToClipboard(e.target.dataset.content, e.target);
            }
        });

        // 收藏功能
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('favorite-button')) {
                this.favoriteReply(e.target.dataset.content, e.target);
            }
        });

        // 使用收藏
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('use-favorite')) {
                this.useFavorite(e.target.dataset.command, e.target);
            }
        });
    }

    setupHTMXEvents() {
        // HTMX 请求开始
        document.addEventListener('htmx:beforeRequest', (event) => {
            this.updateStatus('处理中...', 'warning');
        });

        // HTMX 请求成功
        document.addEventListener('htmx:afterRequest', (event) => {
            if (event.detail.successful) {
                this.updateStatus('就绪', 'success');
                this.scrollToBottom();
            } else {
                this.updateStatus('错误', 'danger');
            }
        });

        // HTMX 错误处理
        document.addEventListener('htmx:responseError', (event) => {
            this.updateStatus('请求失败', 'danger');
            this.showError('网络请求失败，请检查连接');
        });

        // 表单提交后清空输入
        document.addEventListener('htmx:afterRequest', (event) => {
            if (event.detail.elt.tagName === 'FORM' && event.detail.successful) {
                const form = event.detail.elt;
                if (form.querySelector('[name="message"]')) {
                    form.reset();
                    this.updateCharCount();
                }
            }
        });
    }

    updateCharCount() {
        if (!this.elements.messageInput || !this.elements.charCount) return;

        const count = this.elements.messageInput.value.length;
        this.elements.charCount.textContent = count;

        if (count > 900) {
            this.elements.charCount.style.color = '#dc3545';
        } else if (count > 800) {
            this.elements.charCount.style.color = '#fd7e14';
        } else {
            this.elements.charCount.style.color = '#6c757d';
        }
    }

    updateStatus(text, type = 'secondary') {
        if (this.elements.status) {
            this.elements.status.textContent = text;
            this.elements.status.className = `text-${type}`;
        }
    }

    scrollToBottom() {
        if (this.elements.chatMessages) {
            setTimeout(() => {
                this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
            }, 100);
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message error-message';
        errorDiv.innerHTML = `
            <div class="message-content">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </div>
        `;
        
        if (this.elements.chatMessages) {
            this.elements.chatMessages.appendChild(errorDiv);
            this.scrollToBottom();
        }
    }

    copyToClipboard(text, button) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                this.showCopySuccess(button);
            }).catch(err => {
                console.error('复制失败:', err);
                this.fallbackCopyToClipboard(text, button);
            });
        } else {
            this.fallbackCopyToClipboard(text, button);
        }
    }

    fallbackCopyToClipboard(text, button) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            this.showCopySuccess(button);
        } catch (err) {
            console.error('复制失败:', err);
        }

        document.body.removeChild(textArea);
    }

    showCopySuccess(button) {
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.add('copied');

        setTimeout(() => {
            button.innerHTML = originalIcon;
            button.classList.remove('copied');
        }, 2000);
    }

    async favoriteReply(content, button) {
        try {
            const formData = new FormData();
            formData.append('command', content.substring(0, 50) + '...');
            formData.append('description', content);
            formData.append('category', 'AI回复');

            const response = await fetch('/api/favorites', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save favorite');
            }

            this.showFavoriteSuccess(button);
        } catch (error) {
            console.error('Error favoriting reply:', error);
            if (error.message.includes('已存在')) {
                alert('该回复已存在于收藏夹中');
            } else {
                alert('收藏回复失败');
            }
        }
    }

    showFavoriteSuccess(button) {
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.classList.add('favorited');

        setTimeout(() => {
            button.innerHTML = originalIcon;
            button.classList.remove('favorited');
        }, 2000);
    }

    useFavorite(content, button) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(content).then(() => {
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> 已复制';
                setTimeout(() => {
                    button.innerHTML = originalText;
                }, 2000);
            }).catch(err => {
                console.error('复制失败:', err);
                alert('复制失败');
            });
        } else {
            this.fallbackCopyToClipboard(content, button);
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.htmxApp = new HTMXApp();
});

// 全局 HTMX 配置
document.addEventListener('DOMContentLoaded', () => {
    // 设置 HTMX 默认配置
    htmx.config.defaultSwapStyle = 'innerHTML';
    htmx.config.defaultSwapDelay = 0;
    htmx.config.defaultSettleDelay = 20;
});