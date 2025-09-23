import React, { useState, useEffect } from 'react';
import { profileAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, TrendingDown, Users, Heart, MessageCircle, Eye, Loader2 } from 'lucide-react';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await profileAPI.getDashboard();
        setDashboardData(response.data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Erro ao carregar dados do dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  const stats = dashboardData?.stats || {};
  const charts = dashboardData?.charts || {};

  const statCards = [
    {
      title: 'Seguidores',
      value: stats.followers_count?.toLocaleString() || '0',
      change: stats.followers_growth || 0,
      icon: Users,
      color: 'text-blue-600',
    },
    {
      title: 'Taxa de Engajamento',
      value: `${(stats.avg_engagement_rate || 0).toFixed(2)}%`,
      change: stats.engagement_growth || 0,
      icon: Heart,
      color: 'text-red-600',
    },
    {
      title: 'Total de Curtidas',
      value: stats.total_likes?.toLocaleString() || '0',
      change: 0,
      icon: Heart,
      color: 'text-pink-600',
    },
    {
      title: 'Total de Comentários',
      value: stats.total_comments?.toLocaleString() || '0',
      change: 0,
      icon: MessageCircle,
      color: 'text-green-600',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">
          Visão geral da sua performance nas redes sociais
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          const isPositive = stat.change >= 0;
          
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                {stat.change !== 0 && (
                  <p className="text-xs text-muted-foreground flex items-center mt-1">
                    {isPositive ? (
                      <TrendingUp className="h-3 w-3 mr-1 text-green-600" />
                    ) : (
                      <TrendingDown className="h-3 w-3 mr-1 text-red-600" />
                    )}
                    <span className={isPositive ? 'text-green-600' : 'text-red-600'}>
                      {Math.abs(stat.change).toFixed(1)}%
                    </span>
                    <span className="ml-1">vs. mês anterior</span>
                  </p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Followers Evolution */}
        <Card>
          <CardHeader>
            <CardTitle>Evolução de Seguidores</CardTitle>
            <CardDescription>
              Crescimento de seguidores nos últimos 30 dias
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={charts.followers_evolution || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString('pt-BR')}
                    formatter={(value) => [value.toLocaleString(), 'Seguidores']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Engagement Evolution */}
        <Card>
          <CardHeader>
            <CardTitle>Taxa de Engajamento</CardTitle>
            <CardDescription>
              Evolução do engajamento nos últimos 30 dias
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={charts.engagement_evolution || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString('pt-BR')}
                    formatter={(value) => [`${value.toFixed(2)}%`, 'Engajamento']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Reach Evolution */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Evolução do Alcance</CardTitle>
            <CardDescription>
              Alcance dos seus posts nos últimos 30 dias
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={charts.reach_evolution || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString('pt-BR')}
                    formatter={(value) => [value.toLocaleString(), 'Alcance']}
                  />
                  <Bar 
                    dataKey="value" 
                    fill="#10b981"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Próximos Passos</CardTitle>
          <CardDescription>
            Sugestões para melhorar sua performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-border rounded-lg">
              <h3 className="font-semibold mb-2">Conectar Instagram</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Conecte sua conta do Instagram para começar a coletar dados
              </p>
              <button className="text-sm text-primary hover:underline">
                Conectar agora →
              </button>
            </div>
            <div className="p-4 border border-border rounded-lg">
              <h3 className="font-semibold mb-2">Gerar Relatório</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Crie um relatório detalhado da sua performance
              </p>
              <button className="text-sm text-primary hover:underline">
                Gerar relatório →
              </button>
            </div>
            <div className="p-4 border border-border rounded-lg">
              <h3 className="font-semibold mb-2">Ver Feedback</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Confira o feedback dos seus posts mais recentes
              </p>
              <button className="text-sm text-primary hover:underline">
                Ver feedback →
              </button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

