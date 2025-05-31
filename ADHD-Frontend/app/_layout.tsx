import React from "react";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen 
        name="index" 
        options={{
          title: 'ADHD Companion'
        }}
      />
      <Stack.Screen 
        name="session" 
        options={{
          title: 'AI Voice Mode'
        }}
      />
    </Stack>
  );
}
