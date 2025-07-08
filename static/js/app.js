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
        rightMeta.innerHTML = `
            <span class="response-time">⏱️ ${responseTime.toFixed(2)}s</span>
            <span class="thinking-mode">(${mode})</span>
        `;

        // 添加复制按钮到右侧元数据中
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = '复制回答';
        copyButton.onclick = () => this.copyToClipboard(content, copyButton);

        // 将复制按钮添加到右侧元数据中
        rightMeta.appendChild(copyButton);

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

        navigator.clipboard.writeText(plainText).then(() => {
            // 成功复制的视觉反馈
            const originalIcon = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.classList.add('copied');

            setTimeout(() => {
                button.innerHTML = originalIcon;
                button.classList.remove('copied');
            }, 2000);
        }).catch(err => {
            console.error('复制失败:', err);
            // 降级处理：使用传统方法
            this.fallbackCopyToClipboard(plainText, button);
        });
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
            const originalIcon = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.classList.add('copied');

            setTimeout(() => {
                button.innerHTML = originalIcon;
                button.classList.remove('copied');
            }, 2000);
        } catch (err) {
            console.error('降级复制也失败:', err);
        }

        document.body.removeChild(textArea);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new RequirementOptimizerApp();
});