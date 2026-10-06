import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, SafeAreaView, StatusBar, TextInput } from 'react-native';

export default function App() {
  const [model, setModel] = useState<'qwen' | 'llama' | 'cloud'>('qwen');
  const [status, setStatus] = useState('ONLINE (ON-DEVICE)');
  const [input, setInput] = useState('');
  const [logs, setLogs] = useState<string[]>([
    '[ELYRA_RUNTIME: INITIALIZED]',
    '• Model Backend: Qwen 2.5 3B (ARM64 Optimized)',
    '• Memory: Sliding-Window 2,048 Tokens Active',
    '• Hardware Triage: All Sensors Nominal',
  ]);

  const runTriage = () => {
    const newLog = `[TELEMETRY_SCAN @ ${new Date().toLocaleTimeString()}]\n• Battery: 86% (Thermal 29.4°C)\n• CPU Load: 12.4%\n• Token Budget: 312/2048 Tokens\n• Anomaly Count: 0`;
    setLogs(prev => [newLog, ...prev]);
  };

  const sendQuery = () => {
    if (!input.trim()) return;
    const userLog = `> ${input}`;
    const assistantLog = `[ELYRA_${model.toUpperCase()}]: Processed query with edge routing. Context window intact.`;
    setLogs(prev => [assistantLog, userLog, ...prev]);
    setInput('');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#050811" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.brandRow}>
          <Text style={styles.logo}>⚡ ELYRA Mobile</Text>
          <View style={styles.badge}>
            <Text style={styles.badgeText}>APK v1.0.0</Text>
          </View>
        </View>
        <Text style={styles.subtitle}>Edge AI Runtime &amp; Telemetry Assistant</Text>
      </View>

      {/* Model Selector */}
      <View style={styles.modelRow}>
        <TouchableOpacity 
          style={[styles.modelBtn, model === 'qwen' && styles.modelBtnActive]} 
          onPress={() => setModel('qwen')}
        >
          <Text style={[styles.modelBtnText, model === 'qwen' && styles.modelBtnTextActive]}>Qwen 2.5 (3B)</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.modelBtn, model === 'llama' && styles.modelBtnActive]} 
          onPress={() => setModel('llama')}
        >
          <Text style={[styles.modelBtnText, model === 'llama' && styles.modelBtnTextActive]}>Llama 3.2 (GGUF)</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.modelBtn, model === 'cloud' && styles.modelBtnActive]} 
          onPress={() => setModel('cloud')}
        >
          <Text style={[styles.modelBtnText, model === 'cloud' && styles.modelBtnTextActive]}>Cloud Fallback</Text>
        </TouchableOpacity>
      </View>

      {/* Quick Action Button */}
      <TouchableOpacity style={styles.triageBtn} onPress={runTriage}>
        <Text style={styles.triageBtnText}>⚡ Execute Hardware Telemetry Triage</Text>
      </TouchableOpacity>

      {/* Terminal Log Output */}
      <ScrollView style={styles.terminalContainer}>
        {logs.map((log, index) => (
          <View key={index} style={styles.logBox}>
            <Text style={styles.logText}>{log}</Text>
          </View>
        ))}
      </ScrollView>

      {/* Input Bar */}
      <View style={styles.inputRow}>
        <TextInput
          style={styles.textInput}
          placeholder="Ask ELYRA on-device..."
          placeholderTextColor="#64748b"
          value={input}
          onChangeText={setInput}
          onSubmitEditing={sendQuery}
        />
        <TouchableOpacity style={styles.sendBtn} onPress={sendQuery}>
          <Text style={styles.sendBtnText}>Send</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050811',
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  header: {
    marginBottom: 16,
  },
  brandRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    fontSize: 20,
    fontWeight: '800',
    color: '#f8fafc',
    letterSpacing: -0.5,
  },
  badge: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    borderColor: 'rgba(16, 185, 129, 0.3)',
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  badgeText: {
    color: '#10b981',
    fontSize: 11,
    fontWeight: '700',
    fontFamily: 'monospace',
  },
  subtitle: {
    fontSize: 12,
    color: '#38bdf8',
    marginTop: 2,
    fontFamily: 'monospace',
  },
  modelRow: {
    flexDirection: 'row',
    gap: 6,
    marginBottom: 12,
  },
  modelBtn: {
    flex: 1,
    backgroundColor: '#0f172a',
    borderColor: '#1e293b',
    borderWidth: 1,
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: 'center',
  },
  modelBtnActive: {
    backgroundColor: '#38bdf8',
    borderColor: '#38bdf8',
  },
  modelBtnText: {
    color: '#94a3b8',
    fontSize: 11,
    fontWeight: '600',
  },
  modelBtnTextActive: {
    color: '#041220',
    fontWeight: '800',
  },
  triageBtn: {
    backgroundColor: 'rgba(56, 189, 248, 0.12)',
    borderColor: 'rgba(56, 189, 248, 0.3)',
    borderWidth: 1,
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  triageBtnText: {
    color: '#38bdf8',
    fontSize: 13,
    fontWeight: '700',
  },
  terminalContainer: {
    flex: 1,
    backgroundColor: '#02040a',
    borderColor: '#1e293b',
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
  },
  logBox: {
    marginBottom: 8,
  },
  logText: {
    color: '#38bdf8',
    fontFamily: 'monospace',
    fontSize: 12,
    lineHeight: 18,
  },
  inputRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  textInput: {
    flex: 1,
    backgroundColor: '#0f172a',
    borderColor: '#1e293b',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    color: '#f8fafc',
    fontSize: 13,
  },
  sendBtn: {
    backgroundColor: '#38bdf8',
    paddingHorizontal: 16,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendBtnText: {
    color: '#041220',
    fontWeight: '700',
    fontSize: 13,
  },
});
