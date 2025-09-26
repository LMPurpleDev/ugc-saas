// src/pages/Login.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { TrendingUp, Loader2 } from "lucide-react";

const Login = () => {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const result = await login(formData.email, formData.password);
    if (result.success) navigate("/dashboard");
    else setError(result.error);

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center">
            <TrendingUp className="h-12 w-12 text-primary" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-foreground">Entre na sua conta</h2>
          <p className="mt-2 text-sm text-muted-foreground">Acesse sua plataforma UGC SaaS</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Login</CardTitle>
            <CardDescription>Digite suas credenciais</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" name="email" type="email" required value={formData.email} onChange={handleChange} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Senha</Label>
                <Input id="password" name="password" type="password" required value={formData.password} onChange={handleChange} />
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Entrando...</> : "Entrar"}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-muted-foreground">
              Não tem uma conta? <Link to="/register" className="font-medium text-primary hover:text-primary/80">Cadastre-se</Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;
