import { useEffect, useRef, useState } from "react";

import { Message } from "@/lib/types";
import { arrayBufferToBase64, base64ToArrayBuffer } from "@/lib/utils";

export function useWebsocket({
  url = "ws://localhost:4000/ws", // ✅ Changé de 8000 vers 4000
  onNewAudio,
  onAudioDone,
}: {
  url?: string;
  onNewAudio?: (audio: Int16Array<ArrayBuffer>) => void;
  onAudioDone?: () => void;
} = {}) {
  url =
    url ??
    process.env.NEXT_PUBLIC_WEBSOCKET_ENDPOINT ??
    "ws://localhost:8000/ws";
  const [isReady, setIsReady] = useState(false);
  const [history, setHistory] = useState<Message[]>([]);
  const [agentName, setAgentName] = useState<string | null>(null);
  const websocket = useRef<WebSocket | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.addEventListener("open", () => {
      setIsReady(true);
    });
    ws.addEventListener("close", () => {
      setIsReady(false);
    });
    ws.addEventListener("error", (event) => {
      setIsReady(false);
      setIsLoading(false);
      console.error("Websocket error", event);
    });
    ws.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "history.updated") {
        if (data.inputs[data.inputs.length - 1].role !== "user") {
          setIsLoading(false);
        }
        setHistory(data.inputs);
        if (data.agent_name) {
          setAgentName(data.agent_name);
        }
      } else if (data.type === "response.audio.delta") {
        const audioData = new Int16Array(base64ToArrayBuffer(data.delta));
        if (typeof onNewAudio === "function") {
          onNewAudio(audioData);
        }
      } else if (data.type === "audio.done") {
        if (typeof onAudioDone === "function") {
          onAudioDone();
        }
      } else if (data.type === "agent.transfer") {
        // Gestion des transferts d'agents
        console.log("Agent transfer:", data);
        if (data.agent_name) {
          setAgentName(data.agent_name);
        }
      }
    });

    websocket.current = ws;
  }, [url, onNewAudio, onAudioDone]);

  useEffect(() => {
    return () => {
      websocket.current?.close();
    };
  }, []);

  const sendTextMessage = (message: string) => {
    // Vérifier que le WebSocket est ouvert avant d'envoyer
    if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
      websocket.current.send(
        JSON.stringify({
          type: "history.update",
          inputs: [
            ...history,
            {
              role: "user",
              content: message,
              type: "message",
            } as Message,
          ],
        })
      );
    } else {
      console.warn("Cannot send message: WebSocket not ready", {
        readyState: websocket.current?.readyState,
        states: {
          0: "CONNECTING",
          1: "OPEN",
          2: "CLOSING",
          3: "CLOSED",
        },
      });
      // Optionnel : tenter de reconnecter
      if (websocket.current?.readyState === WebSocket.CLOSED) {
        setIsLoading(true);
        // Le useEffect se chargera de reconnecter
      }
    }
  };

  const resetHistory = () => {
    // Même vérification pour reset
    if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
      websocket.current.send(
        JSON.stringify({
          type: "history.update",
          inputs: [],
          reset_agent: true,
        })
      );
    } else {
      console.warn("Cannot reset: WebSocket not ready", websocket.current?.readyState);
    }
  };
  function sendAudioMessage(audio: Int16Array<ArrayBuffer>) {
    if (!websocket.current) {
      throw new Error("Websocket not connected");
    }
    websocket.current.send(
      JSON.stringify({
        type: "history.update",
        inputs: history,
      })
    );
    websocket.current.send(
      JSON.stringify({
        type: "input_audio_buffer.append",
        delta: arrayBufferToBase64(audio.buffer),
      })
    );
    websocket.current.send(
      JSON.stringify({
        type: "input_audio_buffer.commit",
      })
    );
  }

  return {
    isReady,
    sendTextMessage,
    sendAudioMessage,
    history,
    resetHistory,
    agentName,
    isLoading,
  };
}
