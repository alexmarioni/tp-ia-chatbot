import 'dart:async';
import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../services/chat_service.dart';
import '../widgets/message_bubble.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _service = ChatService();
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final _messages = <ChatMessage>[];

  late String _sessionId;
  bool _sessionActive = true;
  bool _isLoading = false;

  Timer? _inactivityTimer;
  Timer? _closeTimer;

  static const _warningDelay = Duration(seconds: 30);
  static const _closeDelay = Duration(seconds: 15);

  @override
  void initState() {
    super.initState();
    _sessionId = const Uuid().v4();
    _addBotMessage(
      '¡Hola! Soy tu asistente de clima. '
      'Preguntame el tiempo en cualquier ciudad, por ejemplo: '
      '"¿Cómo está el clima en Rosario?"',
    );
  }

  @override
  void dispose() {
    _inactivityTimer?.cancel();
    _closeTimer?.cancel();
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _addBotMessage(String text) {
    setState(() {
      _messages.add(ChatMessage(text: text, sender: MessageSender.bot));
    });
    _scrollToBottom();
  }

  void _addUserMessage(String text) {
    setState(() {
      _messages.add(ChatMessage(text: text, sender: MessageSender.user));
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _resetInactivityTimer() {
    _inactivityTimer?.cancel();
    _closeTimer?.cancel();
    _inactivityTimer = Timer(_warningDelay, _onInactivityWarning);
  }

  void _onInactivityWarning() {
    if (!_sessionActive) return;
    _addBotMessage('¿Sigues ahí? En 15 segundos cierro la conversación.');
    _closeTimer = Timer(_closeDelay, _onInactivityClose);
  }

  Future<void> _onInactivityClose() async {
    if (!_sessionActive) return;
    try {
      await _service.closeSession(_sessionId);
    } catch (_) {}
    setState(() => _sessionActive = false);
    _addBotMessage('Conversación cerrada por inactividad. Presioná "Nueva conversación" para continuar.');
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _isLoading || !_sessionActive) return;

    _controller.clear();
    _addUserMessage(text);
    setState(() => _isLoading = true);
    _resetInactivityTimer();

    try {
      final result = await _service.sendMessage(_sessionId, text);
      _addBotMessage(result['reply'] as String);
      if (result['session_active'] == false) {
        setState(() => _sessionActive = false);
        _inactivityTimer?.cancel();
        _closeTimer?.cancel();
      }
    } catch (e) {
      _addBotMessage('Error al conectar con el servidor. Verificá que el backend esté corriendo.');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _startNewSession() {
    _inactivityTimer?.cancel();
    _closeTimer?.cancel();
    setState(() {
      _sessionId = const Uuid().v4();
      _sessionActive = true;
      _messages.clear();
    });
    _addBotMessage(
      '¡Nueva conversación iniciada! '
      'Preguntame el tiempo en cualquier ciudad.',
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.cloud, size: 22),
            SizedBox(width: 8),
            Text('Chatbot de Clima'),
          ],
        ),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          if (!_sessionActive)
            Container(
              width: double.infinity,
              color: Theme.of(context).colorScheme.errorContainer,
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
              child: Row(
                children: [
                  Icon(Icons.info_outline,
                      color: Theme.of(context).colorScheme.onErrorContainer),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Sesión cerrada',
                      style: TextStyle(
                          color: Theme.of(context).colorScheme.onErrorContainer),
                    ),
                  ),
                  TextButton(
                    onPressed: _startNewSession,
                    child: const Text('Nueva conversación'),
                  ),
                ],
              ),
            ),
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: _messages.length,
              itemBuilder: (_, i) => MessageBubble(message: _messages[i]),
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 4),
              child: LinearProgressIndicator(),
            ),
          _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildInputBar() {
    return SafeArea(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.08),
              blurRadius: 4,
              offset: const Offset(0, -2),
            )
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                enabled: _sessionActive && !_isLoading,
                onSubmitted: (_) => _sendMessage(),
                decoration: InputDecoration(
                  hintText: _sessionActive
                      ? '¿Cómo está el clima en...?'
                      : 'Sesión cerrada',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  filled: true,
                  fillColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                ),
                textInputAction: TextInputAction.send,
              ),
            ),
            const SizedBox(width: 8),
            IconButton.filled(
              onPressed: (_sessionActive && !_isLoading) ? _sendMessage : null,
              icon: const Icon(Icons.send),
              style: IconButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.primary,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
