import 'package:flutter/material.dart';

enum MessageSender { user, bot }

class ChatMessage {
  final String text;
  final MessageSender sender;
  final DateTime time;

  ChatMessage({
    required this.text,
    required this.sender,
    DateTime? time,
  }) : time = time ?? DateTime.now();
}

class MessageBubble extends StatelessWidget {
  final ChatMessage message;

  const MessageBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.sender == MessageSender.user;
    final color = isUser
        ? Theme.of(context).colorScheme.primary
        : Theme.of(context).colorScheme.surfaceContainerHighest;
    final textColor = isUser ? Colors.white : Theme.of(context).colorScheme.onSurface;
    final timeStr =
        '${message.time.hour.toString().padLeft(2, '0')}:${message.time.minute.toString().padLeft(2, '0')}';

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 12),
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * (isUser ? 0.75 : 0.85),
        ),
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),
        ),
        child: Column(
          crossAxisAlignment:
              isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            Text(message.text, style: TextStyle(color: textColor, fontSize: 15)),
            const SizedBox(height: 4),
            Text(
              timeStr,
              style: TextStyle(
                color: textColor.withValues(alpha: 0.6),
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
