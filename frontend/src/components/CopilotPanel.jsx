import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Bot,
  Send,
  Plus,
  Paperclip,
  Sparkles,
  FileText,
  AlertCircle,
  CheckCircle,
  HelpCircle,
  X,
} from 'lucide-react';
import {
  sendMessageThunk,
  uploadChatFileThunk,
  initChatSessionThunk,
} from '../store/slices/chatSlice';

export default function CopilotPanel() {
  const dispatch = useDispatch();
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  const { activeChatId, messages, isLoading, isUploading, error } = useSelector(
    (state) => state.chat
  );

  // Auto scroll to bottom when messages update
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Ensure active chat session exists on mount
  useEffect(() => {
    if (!activeChatId) {
      dispatch(initChatSessionThunk());
    }
  }, [activeChatId, dispatch]);

  const handleSendMessage = (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading || !activeChatId) return;

    const messageText = input.trim();
    setInput('');

    dispatch(sendMessageThunk({ chatId: activeChatId, content: messageText }));
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (activeChatId) {
      dispatch(uploadChatFileThunk({ file, chatId: activeChatId }));
    }
    // Reset file input value
    e.target.value = '';
  };

  const handlePromptChipClick = (promptText) => {
    if (!activeChatId || isLoading) return;
    dispatch(sendMessageThunk({ chatId: activeChatId, content: promptText }));
  };

  const quickPrompts = [
    'Apollo Pharmacy reported 50 boxes of discolored Amoxicillin 500mg capsules, batch AMX240602.',
    'Received complaint from City Hospital about sub-potency in Paracetamol 650mg tablets, batch PCT9920.',
    'Customer reported broken seals on 10 bottles of Cough Syrup, manufactured Jan 2026.',
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs flex flex-col h-full overflow-hidden">
      {/* Panel Header */}
      <div className="px-5 py-4 bg-gradient-to-r from-teal-900 via-teal-800 to-slate-900 text-white flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-teal-500/20 rounded-xl backdrop-blur-xs border border-teal-400/30 text-teal-300">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white tracking-wide">AI Copilot Panel</h2>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Active
              </span>
            </div>
            <p className="text-[11px] text-teal-200/80">LLM Structured Extraction & Guidance</p>
          </div>
        </div>

        <div className="text-xs text-teal-200/60 font-mono">
          {activeChatId ? `Chat #${activeChatId}` : 'Initializing...'}
        </div>
      </div>

      {/* Quick Prompts Bar */}
      <div className="px-4 py-2.5 bg-slate-50 border-b border-slate-200/80">
        <div className="text-[11px] font-semibold text-slate-500 mb-1.5 flex items-center gap-1">
          <Sparkles className="h-3 w-3 text-teal-600" />
          Try sample complaint prompts:
        </div>
        <div className="flex flex-wrap gap-1.5">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handlePromptChipClick(prompt)}
              className="text-[11px] px-2.5 py-1 rounded-lg bg-white hover:bg-teal-50 text-slate-700 hover:text-teal-800 border border-slate-200 hover:border-teal-300 transition-all text-left cursor-pointer truncate max-w-full"
            >
              "{prompt.slice(0, 45)}..."
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/40">
        {messages.length === 0 && !isLoading && (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-3">
            <div className="h-12 w-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center">
              <Bot className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-700">AI Copilot is ready</p>
              <p className="text-xs text-slate-500 max-w-xs mt-1">
                Describe the reported customer complaint or upload document attachments using the **+** button.
              </p>
            </div>
          </div>
        )}

        {messages.map((msg, index) => {
          const isUser = msg.sender === 'user';
          const isSystem = msg.sender === 'system';

          if (isSystem) {
            return (
              <div key={msg.id || index} className="flex justify-center my-2">
                <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200 text-xs text-slate-600 font-medium shadow-2xs">
                  <Paperclip className="h-3.5 w-3.5 text-teal-600" />
                  {msg.content}
                </div>
              </div>
            );
          }

          return (
            <div
              key={msg.id || index}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-1`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed shadow-2xs ${
                  isUser
                    ? 'bg-teal-600 text-white rounded-br-none'
                    : 'bg-white text-slate-800 border border-slate-200/90 rounded-bl-none'
                }`}
              >
                {!isUser && (
                  <div className="flex items-center gap-1.5 text-teal-700 font-bold mb-1 text-[11px]">
                    <Bot className="h-3.5 w-3.5 text-teal-600" />
                    <span>AI Copilot</span>
                  </div>
                )}
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Render Structured Extraction Card if returned */}
                {!isUser && msg.extracted_data && msg.extracted_data.is_valid_complaint && (
                  <div className="mt-2.5 p-2.5 bg-teal-50/80 rounded-xl border border-teal-200/80 text-[11px] space-y-1.5 text-slate-700">
                    <div className="font-bold text-teal-900 flex items-center gap-1">
                      <Sparkles className="h-3 w-3 text-teal-600" />
                      Extracted Structured Fields:
                    </div>
                    <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-[10px]">
                      {msg.extracted_data.product_name && (
                        <div><span className="font-semibold">Product:</span> {msg.extracted_data.product_name}</div>
                      )}
                      {msg.extracted_data.batch_number && (
                        <div><span className="font-semibold">Batch:</span> {msg.extracted_data.batch_number}</div>
                      )}
                      {msg.extracted_data.customer_name && (
                        <div><span className="font-semibold">Customer:</span> {msg.extracted_data.customer_name}</div>
                      )}
                      {msg.extracted_data.initial_severity && (
                        <div><span className="font-semibold">Severity:</span> {msg.extracted_data.initial_severity}</div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <span className="text-[10px] text-slate-400 px-1">
                {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
              </span>
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-start space-x-2 my-2">
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-none px-4 py-3 shadow-2xs">
              <div className="flex items-center space-x-2 text-xs text-teal-700 font-semibold mb-1">
                <Bot className="h-3.5 w-3.5" />
                <span>AI Copilot is processing...</span>
              </div>
              <div className="flex items-center space-x-1.5 py-1">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          </div>
        )}

        {/* Uploading File Loading State */}
        {isUploading && (
          <div className="flex justify-center my-2">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-teal-50 border border-teal-200 text-xs text-teal-800 font-medium">
              <div className="h-3 w-3 border-2 border-teal-600 border-t-transparent rounded-full animate-spin" />
              Uploading document attachment...
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input Bar */}
      <div className="p-3 bg-white border-t border-slate-200">
        <form onSubmit={handleSendMessage} className="flex items-center gap-2">
          {/* Traditional File Upload (+) Button on Left of Chat Input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.docx,.doc,.txt,.eml"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading || isLoading || !activeChatId}
            className="h-10 w-10 rounded-xl bg-slate-100 hover:bg-teal-50 text-slate-600 hover:text-teal-700 border border-slate-200 hover:border-teal-300 flex items-center justify-center transition-all cursor-pointer disabled:opacity-50 shrink-0"
            title="Upload file attachment (PDF, DOCX, TXT, EML)"
          >
            <Plus className="h-5 w-5" />
          </button>

          {/* Text Input Field */}
          <input
            type="text"
            placeholder="Type complaint prompt or details for AI parsing..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading || !activeChatId}
            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 disabled:bg-slate-50 transition-all"
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={!input.trim() || isLoading || !activeChatId}
            className="h-10 px-4 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs flex items-center gap-1.5 transition-all disabled:opacity-50 cursor-pointer shadow-sm shrink-0"
          >
            <span>Send</span>
            <Send className="h-3.5 w-3.5" />
          </button>
        </form>
        <div className="text-[10px] text-slate-400 mt-1.5 px-1 flex items-center justify-between">
          <span>Supported attachments: PDF, DOCX, TXT, EML (up to 10MB)</span>
          <span className="text-teal-700 font-medium">Press Enter to send</span>
        </div>
      </div>
    </div>
  );
}
