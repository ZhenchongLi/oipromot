class RequirementOptimizerApp {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.websocket = null;
        this.isConnected = false;
        this.currentStatus = 'IDLE';

        this.initializeElements();
        this.setupEventListeners();
        this.connectWebSocket();
        this.updateSessionId();
        this.initializeAuth();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeElements() {
        this.elements = {
            sessionIdSpan: document.getElementById('session-id'),
            statusSpan: document.getElementById('status'),
            connectionStatusSpan: document.getElementById('connection-status'),
            chatMessages: document.getElementById('chat-messages'),
            messageInput: document.getElementById('message-input'),
            sendButton: document.getElementById('send-button'),
            newConversationButton: document.getElementById('new-conversation'),
            showFavoritesButton: document.getElementById('show-favorites'),

            charCount: document.getElementById('char-count')
        };
    }

    setupEventListeners() {
        // 发送按钮
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());

        // 回车键发送
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // 字符计数
        this.elements.messageInput.addEventListener('input', (e) => {
            this.updateCharCount();
        });

        // 新对话按钮
        this.elements.newConversationButton.addEventListener('click', () => {
            this.startNewConversation();
        });

        // 收藏夹按钮
        this.elements.showFavoritesButton.addEventListener('click', () => {
            this.showFavorites();
        });

        // 收藏夹相关事件
        this.setupFavoriteEvents();
    }

    updateSessionId() {
        this.elements.sessionIdSpan.textContent = this.sessionId.slice(-8);
    }

    updateCharCount() {
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



    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus('已连接', 'success');
            this.updateStatus('就绪', 'success');
            this.elements.sendButton.disabled = false;
            this.elements.messageInput.disabled = false;
        };

        this.websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };

        this.websocket.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus('连接断开', 'danger');
            this.updateStatus('断开连接', 'danger');
            this.elements.sendButton.disabled = true;
            this.elements.messageInput.disabled = true;

            // 尝试重连
            setTimeout(() => {
                if (!this.isConnected) {
                    this.connectWebSocket();
                }
            }, 3000);
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('连接错误', 'danger');
        };
    }

    updateConnectionStatus(text, type = 'secondary') {
        this.elements.connectionStatusSpan.textContent = text;
        this.elements.connectionStatusSpan.className = `text-${type}`;
    }

    updateStatus(text, type = 'secondary') {
        this.elements.statusSpan.textContent = text;
        this.elements.statusSpan.className = `text-${type}`;
    }

    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'processing':
                this.addProcessingMessage(message.content);
                this.updateStatus('处理中...', 'warning');
                break;

            case 'ai_response':
                this.removeProcessingMessage();
                this.addAIMessage(message.content, message.response_time, message.mode);
                this.updateStatus('等待反馈', 'info');
                this.currentStatus = 'WAITING_FEEDBACK';
                break;

            case 'ai_response_refined':
                this.removeProcessingMessage();
                this.addAIMessage(message.content, message.response_time, message.mode, true);
                this.updateStatus('等待反馈', 'info');
                this.currentStatus = 'WAITING_FEEDBACK';
                break;

            case 'error':
                this.removeProcessingMessage();
                this.addErrorMessage(message.content, message.response_time, message.error_type, message.error_suggestion);
                this.updateStatus('错误', 'danger');
                this.currentStatus = 'ERROR';
                break;

            case 'new_conversation':
                this.clearMessages();
                this.addSystemMessage('开始新对话');
                this.updateStatus('就绪', 'success');
                this.currentStatus = 'IDLE';
                break;
        }
    }

    sendMessage() {
        const content = this.elements.messageInput.value.trim();
        if (!content || !this.isConnected) return;

        // 添加用户消息到界面
        this.addUserMessage(content);

        // 清空输入框
        this.elements.messageInput.value = '';
        this.updateCharCount();



        // 发送消息
        this.websocket.send(JSON.stringify({
            type: 'user_input',
            content: content
        }));

        this.updateStatus('发送中...', 'warning');
    }

    startNewConversation() {
        if (!this.isConnected) return;

        this.websocket.send(JSON.stringify({
            type: 'new_conversation'
        }));
    }

    addUserMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        messageDiv.appendChild(contentDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addAIMessage(content, responseTime = 0, mode = '', isRefined = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // 处理换行和格式
        const formattedContent = this.formatContent(content);
        contentDiv.innerHTML = formattedContent;

        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';

        const leftMeta = document.createElement('div');
        leftMeta.innerHTML = `<i class="fas fa-robot"></i> ${isRefined ? 'AI调整后回复' : 'AI回复'}`;

        const rightMeta = document.createElement('div');
        
        // 添加时间和模式信息
        const timeSpan = document.createElement('span');
        timeSpan.className = 'response-time';
        timeSpan.innerHTML = `⏱️ ${responseTime.toFixed(2)}s`;
        
        const modeSpan = document.createElement('span');
        modeSpan.className = 'thinking-mode';
        modeSpan.innerHTML = `(${mode})`;
        
        // 添加复制按钮
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = '复制回答';
        copyButton.onclick = () => this.copyToClipboard(content, copyButton);

        // 添加收藏按钮
        const favoriteButton = document.createElement('button');
        favoriteButton.className = 'favorite-button';
        favoriteButton.innerHTML = '<i class="fas fa-star"></i>';
        favoriteButton.title = '收藏此回复';
        favoriteButton.onclick = () => this.favoriteReply(content, favoriteButton);

        // 将所有元素添加到右侧元数据中
        rightMeta.appendChild(timeSpan);
        rightMeta.appendChild(modeSpan);
        rightMeta.appendChild(copyButton);
        rightMeta.appendChild(favoriteButton);

        metaDiv.appendChild(leftMeta);
        metaDiv.appendChild(rightMeta);

        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(metaDiv);

        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${content}`;

        messageDiv.appendChild(contentDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addErrorMessage(content, responseTime = 0, errorType = '', errorSuggestion = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message error-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Format error content with type if available
        let errorHtml = `<i class="fas fa-exclamation-triangle"></i> ${content}`;

        // Add error type badge if available
        if (errorType) {
            errorHtml += `<br><span class="badge bg-danger mt-2">${errorType}</span>`;
        }

        // Add retry suggestions
        errorHtml += `
            <div class="mt-3 small">
                <strong>🔄 您可以:</strong>
                <ul class="mb-0 mt-1">
                    <li>检查网络连接和配置</li>
                    <li>重新输入需求</li>
                    <li>点击"新对话"重新开始</li>
                </ul>
            </div>
        `;

        contentDiv.innerHTML = errorHtml;

        // Add metadata
        if (responseTime > 0) {
            const metaDiv = document.createElement('div');
            metaDiv.className = 'message-meta';
            metaDiv.innerHTML = `<span class="response-time">⏱️ ${responseTime.toFixed(2)}s</span>`;
            messageDiv.appendChild(metaDiv);
        }

        messageDiv.appendChild(contentDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addProcessingMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message processing-message';
        messageDiv.id = 'processing-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${content}<span class="loading-dots"></span>`;

        messageDiv.appendChild(contentDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    removeProcessingMessage() {
        const processingMessage = document.getElementById('processing-message');
        if (processingMessage) {
            processingMessage.remove();
        }
    }

    clearMessages() {
        this.elements.chatMessages.innerHTML = '';
    }

    formatContent(content) {
        // 处理换行
        let formatted = content.replace(/\n/g, '<br>');

        // 处理编号列表
        formatted = formatted.replace(/^(\d+)\.\s/gm, '<strong>$1.</strong> ');

        // 处理代码块
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

        return formatted;
    }

    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }, 100);
    }

    copyToClipboard(text, button) {
        // 移除HTML标签，获取纯文本
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = this.formatContent(text);
        const plainText = tempDiv.textContent || tempDiv.innerText || '';

        // 检查 navigator.clipboard 是否可用
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(plainText).then(() => {
                // 成功复制的视觉反馈
                this.showCopySuccess(button);
            }).catch(err => {
                console.error('复制失败:', err);
                // 降级处理：使用传统方法
                this.fallbackCopyToClipboard(plainText, button);
            });
        } else {
            // 直接使用降级方法
            this.fallbackCopyToClipboard(plainText, button);
        }
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
            console.error('降级复制也失败:', err);
        }

        document.body.removeChild(textArea);
    }

    // 收藏夹相关功能
    setupFavoriteEvents() {
        // 添加收藏按钮事件
        document.addEventListener('click', (e) => {
            if (e.target.id === 'add-favorite') {
                this.showAddFavoriteModal();
            }
            if (e.target.id === 'saveFavorite') {
                this.saveFavorite();
            }
        });

        // 收藏夹模态框中的事件代理
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('use-favorite')) {
                this.useFavorite(e.target.dataset.command, e.target);
            }
            if (e.target.classList.contains('edit-favorite')) {
                this.editFavorite(e.target.dataset.id);
            }
            if (e.target.classList.contains('delete-favorite')) {
                this.deleteFavorite(e.target.dataset.id);
            }
        });

        // 搜索功能
        document.addEventListener('input', (e) => {
            if (e.target.id === 'search-favorites') {
                this.searchFavorites(e.target.value);
            }
        });
    }

    showFavorites() {
        this.loadFavorites();
        const modal = new bootstrap.Modal(document.getElementById('favoritesModal'));
        modal.show();
        
        // 清空搜索框
        const searchInput = document.getElementById('search-favorites');
        if (searchInput) {
            searchInput.value = '';
        }
    }

    async loadFavorites() {
        try {
            const response = await fetch('/api/favorites', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to load favorites');
            }
            
            const favorites = await response.json();
            this.allFavorites = favorites; // 存储所有收藏以便搜索
            this.renderFavorites(favorites);
        } catch (error) {
            console.error('Error loading favorites:', error);
            document.getElementById('favorites-list').innerHTML = '<div class="alert alert-danger">加载收藏夹失败</div>';
        }
    }

    renderFavorites(favorites) {
        const listContainer = document.getElementById('favorites-list');
        
        if (favorites.length === 0) {
            listContainer.innerHTML = '<div class="alert alert-info">还没有收藏的命令</div>';
            return;
        }

        const html = favorites.map(fav => `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">
                        ${fav.command}
                        ${fav.category ? `<span class="badge bg-secondary ms-2">${fav.category}</span>` : ''}
                    </h6>
                    ${fav.description ? `<p class="card-text" style="max-height: 100px; overflow-y: auto; font-size: 0.9rem;">${fav.description.replace(/\n/g, '<br>')}</p>` : ''}
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-primary use-favorite" data-command="${fav.description || fav.command}">
                            <i class="fas fa-copy"></i> 复制
                        </button>
                        <button class="btn btn-outline-secondary edit-favorite" data-id="${fav.id}">
                            <i class="fas fa-edit"></i> 编辑
                        </button>
                        <button class="btn btn-outline-danger delete-favorite" data-id="${fav.id}">
                            <i class="fas fa-trash"></i> 删除
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        listContainer.innerHTML = html;
    }

    showAddFavoriteModal() {
        document.getElementById('editFavoriteModalTitle').textContent = '添加命令收藏';
        document.getElementById('favoriteForm').reset();
        document.getElementById('favoriteForm').dataset.mode = 'add';
        
        const modal = new bootstrap.Modal(document.getElementById('editFavoriteModal'));
        modal.show();
    }

    async editFavorite(favoriteId) {
        try {
            const response = await fetch(`/api/favorites/${favoriteId}`, {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to load favorite');
            }
            
            const favorite = await response.json();
            
            document.getElementById('editFavoriteModalTitle').textContent = '编辑命令收藏';
            document.getElementById('favoriteCommand').value = favorite.command;
            document.getElementById('favoriteDescription').value = favorite.description || '';
            document.getElementById('favoriteCategory').value = favorite.category || '';
            document.getElementById('favoriteForm').dataset.mode = 'edit';
            document.getElementById('favoriteForm').dataset.id = favoriteId;
            
            const modal = new bootstrap.Modal(document.getElementById('editFavoriteModal'));
            modal.show();
        } catch (error) {
            console.error('Error loading favorite:', error);
            alert('加载收藏命令失败');
        }
    }

    async saveFavorite() {
        const form = document.getElementById('favoriteForm');
        const formData = new FormData();
        
        formData.append('command', document.getElementById('favoriteCommand').value);
        formData.append('description', document.getElementById('favoriteDescription').value);
        formData.append('category', document.getElementById('favoriteCategory').value);
        
        const mode = form.dataset.mode;
        const url = mode === 'add' ? '/api/favorites' : `/api/favorites/${form.dataset.id}`;
        const method = mode === 'add' ? 'POST' : 'PUT';
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Failed to save favorite');
            }
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('editFavoriteModal'));
            modal.hide();
            
            // 重新加载收藏夹列表
            this.loadFavorites();
        } catch (error) {
            console.error('Error saving favorite:', error);
            alert('保存收藏命令失败');
        }
    }

    async deleteFavorite(favoriteId) {
        if (!confirm('确定要删除这个收藏命令吗？')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/favorites/${favoriteId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete favorite');
            }
            
            // 重新加载收藏夹列表
            this.loadFavorites();
        } catch (error) {
            console.error('Error deleting favorite:', error);
            alert('删除收藏命令失败');
        }
    }

    useFavorite(content, button) {
        // 复制到剪贴板
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(content).then(() => {
                // 显示复制成功提示
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
            // 降级处理
            const textArea = document.createElement('textarea');
            textArea.value = content;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="fas fa-check"></i> 已复制';
                    setTimeout(() => {
                        button.innerHTML = originalText;
                    }, 2000);
                } else {
                    alert('复制失败');
                }
            } catch (err) {
                console.error('复制失败:', err);
                alert('复制失败');
            }
            
            document.body.removeChild(textArea);
        }
    }

    async favoriteReply(content, button) {
        // 提取纯文本内容
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = this.formatContent(content);
        const plainText = tempDiv.textContent || tempDiv.innerText || '';
        
        // 生成简短的标题（取前50个字符）
        const title = plainText.substring(0, 50) + (plainText.length > 50 ? '...' : '');
        
        try {
            const formData = new FormData();
            formData.append('command', title);
            formData.append('description', plainText);
            formData.append('category', 'AI回复');
            
            const response = await fetch('/api/favorites', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save favorite');
            }
            
            // 成功收藏的视觉反馈
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

    searchFavorites(query) {
        if (!this.allFavorites) {
            return;
        }
        
        const filteredFavorites = this.allFavorites.filter(fav => 
            fav.command.toLowerCase().includes(query.toLowerCase()) ||
            (fav.description && fav.description.toLowerCase().includes(query.toLowerCase())) ||
            (fav.category && fav.category.toLowerCase().includes(query.toLowerCase()))
        );
        
        this.renderFavorites(filteredFavorites);
    }

    getAuthToken() {
        // 从localStorage获取JWT token
        return localStorage.getItem('authToken') || '';
    }

    // 设置认证token
    setAuthToken(token) {
        if (token) {
            localStorage.setItem('authToken', token);
        } else {
            localStorage.removeItem('authToken');
        }
    }

    // 检查是否已登录
    isAuthenticated() {
        return !!this.getAuthToken();
    }

    // 初始化认证状态
    async initializeAuth() {
        // 如果没有JWT token，尝试通过session获取
        if (!this.getAuthToken()) {
            try {
                // 尝试从session获取JWT token
                const response = await fetch('/api/get-token', {
                    method: 'POST',
                    credentials: 'include' // 包含session cookie
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.setAuthToken(data.access_token);
                    console.log('JWT token obtained from session');
                } else {
                    console.log('No valid session for JWT token');
                }
            } catch (error) {
                console.log('Failed to get JWT token from session:', error);
            }
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new RequirementOptimizerApp();
});