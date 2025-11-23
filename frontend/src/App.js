import React, { useState } from "react";
import { ChakraProvider, Box, Heading, Input, Button, VStack, Spinner, Image, Tabs, TabList, TabPanels, Tab, TabPanel } from "@chakra-ui/react";

function App() {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker }),
      });
      if (!response.ok) throw new Error("Ticker not found or server error");
      const data = await response.json();
      setResults(data);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <ChakraProvider>
      <Box maxW="800px" mx="auto" mt={10} p={6} boxShadow="lg" borderRadius="md">
        <Heading mb={6}>Stock Analysis Dashboard</Heading>
        <VStack spacing={4} align="stretch">
          <Input
            placeholder="Enter Ticker (e.g. AAPL)"
            value={ticker}
            onChange={e => setTicker(e.target.value.toUpperCase())}
            isDisabled={loading}
          />
          <Button colorScheme="teal" onClick={handleSubmit} isLoading={loading} loadingText="Analyzing...">
            Analyze
          </Button>
          {loading && <Spinner size="xl" thickness="4px" color="teal.500" />}
          {error && <Box color="red.500">{error}</Box>}
          {results && (
            <Tabs variant="enclosed" colorScheme="teal">
              <TabList>
                {Object.keys(results).map(name => (
                  <Tab key={name}>{name}</Tab>
                ))}
              </TabList>
              <TabPanels>
                {Object.entries(results).map(([name, res]) => (
                  <TabPanel key={name}>
                    <Heading size="md" mb={4}>{name} Forecast</Heading>
                    <Image src={`http://localhost:8000/graph/${res.plot_id}`} alt={`${name} graph`} mb={4} />
                  </TabPanel>
                ))}
              </TabPanels>
            </Tabs>
          )}
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

export default App;
