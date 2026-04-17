import { useState, useRef, useEffect } from "react";
import { X, Send } from "lucide-react";
import { useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getAccessToken } from "@/lib/auth";
import { apiRequest } from "@/lib/api";

interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  meta?: {
    confidence?: number;
    sourceLabel?: string;
    reinforcementTopics?: string[];
  };
}

interface CorpusItem {
  id: number;
  categoria: string;
  pregunta: string;
  respuesta: string;
  score: number;
}

interface ChatbotQueryResponse {
  answer: string;
  found: boolean;
  results: CorpusItem[];
}

interface ChatbotQueryContextResponse {
  answer: string;
  found: boolean;
  confidence: number;
  sources: CorpusItem[];
  context: {
    skill_level: number | null;
    recent_error_topics: string[];
  };
}

const FloatingChatbot = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "0",
      type: "bot",
      content:
        "¡Hola! Soy el asistente ECG. Puedo ayudarte con preguntas sobre arritmias, interpretación de ECG, definiciones y mucho más. ¿Qué deseas saber?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const iconVersionRef = useRef(Date.now());
  const primaryIconUrl = `${import.meta.env.BASE_URL}medical_chat_icon_1.svg?v=${iconVersionRef.current}`;
  const fallbackIconUrl = `${import.meta.env.BASE_URL}medical_chat_icon_2.svg?v=${iconVersionRef.current}`;
  const [iconUrl, setIconUrl] = useState(primaryIconUrl);
  const showOnRoutes = location.pathname === "/dashboard" || location.pathname === "/library";

  useEffect(() => {
    // Reinicia el icono cuando cambia la ruta para evitar estado de fallback persistente.
    setIconUrl(primaryIconUrl);
  }, [location.pathname, primaryIconUrl]);

  useEffect(() => {
    // Verificar autenticación cada vez que cambia la ubicación
    const token = getAccessToken();
    setIsAuthenticated(!!token);
  }, [location]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await apiRequest<ChatbotQueryContextResponse>("/chatbot/query-context", {
        method: "POST",
        body: {
          question: input,
          top_k: 3,
        },
      });

      const primarySource = response.sources?.[0];
      const reinforcementTopics = (response.context?.recent_error_topics ?? []).slice(0, 3);
      const sourceLabel = primarySource
        ? `${primarySource.categoria.replaceAll("_", " ")} (id ${primarySource.id})`
        : undefined;

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: response.answer,
        meta: {
          confidence: response.confidence,
          sourceLabel,
          reinforcementTopics,
        },
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content:
          error instanceof Error
            ? `No pude responder ahora mismo: ${error.message}`
            : "No pude responder ahora mismo. Intenta de nuevo en unos segundos.",
      };
      setMessages((prev) => [...prev, botMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button - Solo mostrar si está autenticado */}
      {isAuthenticated && showOnRoutes && (
        <>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="fixed bottom-6 right-6 z-40 flex items-center justify-center w-20 h-20 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 overflow-hidden"
            aria-label="Chat medico"
          >
            <img
              src={iconUrl}
              alt="Chat medico"
              className="w-full h-full object-cover"
              onError={() => {
                if (iconUrl !== fallbackIconUrl) {
                  setIconUrl(fallbackIconUrl);
                }
              }}
            />
          </button>

          {/* Chat Window */}
          {isOpen && (
            <div className="fixed bottom-24 right-6 z-50 w-96 bg-white rounded-lg shadow-2xl border border-border overflow-hidden flex flex-col max-h-96">
              {/* Header con fondo del icono */}
              <div
                className="text-white p-4 flex items-center justify-between"
                style={{
                  backgroundImage:
                    "linear-gradient(135deg, #1A7A8A 0%, #0D5F6E 100%)",
                }}
              >
                <div>
                  <h3 className="font-semibold">Asistente ECG</h3>
                  <p className="text-xs text-white/90">Powered by Backend TF-IDF</p>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:text-white/80"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.type === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                        message.type === "user"
                          ? "bg-primary text-white rounded-br-none"
                          : "bg-white border border-border text-foreground rounded-bl-none"
                      }`}
                    >
                      <p className="break-words">{message.content}</p>
                      {message.type === "bot" && message.meta && (
                        <div className="mt-2 space-y-1 text-[10px] text-muted-foreground border-t pt-2">
                          {message.meta.sourceLabel && (
                            <p>Fuente: {message.meta.sourceLabel}</p>
                          )}
                          {!!message.meta.reinforcementTopics?.length && (
                            <p>
                              Reforzar: {message.meta.reinforcementTopics.join(", ").replaceAll("_", " ")}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-border px-4 py-2 rounded-lg rounded-bl-none">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-4 border-t border-border bg-white flex gap-2">
                <Input
                  placeholder="Pregunta sobre ECG..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      handleSendMessage();
                    }
                  }}
                  disabled={isLoading}
                  className="text-sm"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isLoading || !input.trim()}
                  size="sm"
                  className="px-3"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </>
  );
};

export default FloatingChatbot;
