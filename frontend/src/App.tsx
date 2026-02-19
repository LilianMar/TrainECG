import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import ClassifyECG from "./pages/ClassifyECG";
import PracticeMode from "./pages/PracticeMode";
import InitialTest from "./pages/InitialTest";
import PostPracticeTest from "./pages/PostPracticeTest";
import Progress from "./pages/Progress";
import Profile from "./pages/Profile";
import Library from "./pages/Library";
import NotFound from "./pages/NotFound";
import FloatingChatbot from "./components/FloatingChatbot";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/classify" element={<ProtectedRoute><ClassifyECG /></ProtectedRoute>} />
          <Route path="/practice" element={<ProtectedRoute><PracticeMode /></ProtectedRoute>} />
          <Route path="/progress" element={<ProtectedRoute><Progress /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/test" element={<ProtectedRoute><InitialTest /></ProtectedRoute>} />
          <Route path="/test-evaluation" element={<ProtectedRoute><PostPracticeTest /></ProtectedRoute>} />
          <Route path="/library" element={<ProtectedRoute><Library /></ProtectedRoute>} />
          {/* Catch-all route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
        <FloatingChatbot />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
