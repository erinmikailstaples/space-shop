import { useState } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Text,
  Container,
  useToast,
  Link,
  Stack,
} from '@chakra-ui/react';
import axios from 'axios';

interface Message {
  text: string;
  isUser: boolean;
  sources?: string[];
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const handleSend = async () => {
    if (!input.trim()) return;

    try {
      setIsLoading(true);
      // Add user message
      setMessages(prev => [...prev, { text: input, isUser: true }]);

      // Send message to backend
      const response = await axios.post('http://localhost:8000/chat', {
        message: input
      });

      // Add bot response
      setMessages(prev => [...prev, {
        text: response.data.response,
        isUser: false,
        sources: response.data.sources
      }]);

      setInput('');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to send message',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.md" py={8}>
      <Stack spacing={4} align="stretch" h="80vh">
        <Box
          flex={1}
          overflowY="auto"
          borderWidth={1}
          borderRadius="lg"
          p={4}
          bg="gray.50"
        >
          {messages.map((message, index) => (
            <Box
              key={index}
              mb={4}
              bg={message.isUser ? 'blue.100' : 'white'}
              p={3}
              borderRadius="lg"
            >
              <Text>{message.text}</Text>
              {message.sources && (
                <Box mt={2}>
                  <Text fontSize="sm" color="gray.600">Sources:</Text>
                  {message.sources.map((source, idx) => (
                    <Link
                      key={idx}
                      href={source}
                      color="blue.500"
                      fontSize="sm"
                      display="block"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {source}
                    </Link>
                  ))}
                </Box>
              )}
            </Box>
          ))}
        </Box>
        <Box>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about Jupiter's moons..."
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
          />
          <Button
            mt={2}
            colorScheme="blue"
            onClick={handleSend}
            _loading={isLoading}
            w="full"
          >
            Send
          </Button>
        </Box>
      </Stack>
    </Container>
  );
} 