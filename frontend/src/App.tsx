import { ChakraProvider, Box, Heading, ThemeProvider } from '@chakra-ui/react'
import { Chat } from './components/Chat'

function App() {
  return (
    <ThemeProvider>
      <ChakraProvider>
        <Box p={8}>
          <Heading mb={8} textAlign="center">Jupiter Moons Chatbot</Heading>
          <Chat />
        </Box>
      </ChakraProvider>
    </ThemeProvider>
  )
}

export default App
