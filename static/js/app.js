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
            thinkModeCheckbox: document.getElementById('think-mode'),
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
        
        // 思考模式切换
        this.elements.thinkModeCheckbox.addEventListener('change', () => {
            this.updateThinkModeStatus();
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
    
    updateThinkModeStatus() {
        const isThinkMode = this.elements.thinkModeCheckbox.checked;
        if (isThinkMode) {
            this.elements.messageInput.placeholder = '请输入您的需求（思考模式已启用）...';
        } else {
            this.elements.messageInput.placeholder = '请输入您的需求...';
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
                this.addErrorMessage(message.content, message.response_time);
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
        
        // 处理思考模式
        let processedContent = content;
        if (this.elements.thinkModeCheckbox.checked && !content.includes('/t')) {
            processedContent = '/t ' + content;
        }
        
        // 发送消息
        const messageType = this.currentStatus === 'IDLE' ? 'new_requirement' : 'feedback';
        this.websocket.send(JSON.stringify({
            type: messageType,
            content: processedContent
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
    
    addErrorMessage(content, responseTime = 0) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message error-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${content}`;
        
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
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new RequirementOptimizerApp();
});