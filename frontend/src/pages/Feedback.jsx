import React, { useState, useEffect } from 'react';
import { feedbackAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { MessageSquare, Star, TrendingUp, Eye, ExternalLink, Loader2 } from 'lucide-react';

const Feedback = () => {
  const [feedback, setFeedback] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [feedbackResponse, summaryResponse] = await Promise.all([
          feedbackAPI.getFeedback({ limit: 20 }),
          feedbackAPI.getFeedbackSummary(),
        ]);
        
        setFeedback(feedbackResponse.data);
        setSummary(summaryResponse.data);
      } catch (err) {
        console.error('Error fetching feedback data:', err);
        setError('Erro ao carregar dados de feedback');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 8) return 'Excelente';
    if (score >= 6) return 'Bom';
    if (score >= 4) return 'Regular';
    return 'Precisa melhorar';
  };

  const formatScore = (score) => {
    return (score * 10).toFixed(1);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Feedback dos Posts</h1>
        <p className="text-muted-foreground">
          Análise detalhada e sugestões para seus posts
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Posts Analisados</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_posts_analyzed}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Nota Geral Média</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatScore(summary.average_scores.overall)}
              </div>
              <p className="text-xs text-muted-foreground">
                {getScoreLabel(summary.average_scores.overall)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Melhor Post</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {formatScore(summary.best_post_score)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Engajamento Médio</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatScore(summary.average_scores.engagement_potential)}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Average Scores Breakdown */}
      {summary && (
        <Card>
          <CardHeader>
            <CardTitle>Breakdown das Notas Médias</CardTitle>
            <CardDescription>
              Análise detalhada das suas métricas de performance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Qualidade do Conteúdo</span>
                  <span className="text-sm text-muted-foreground">
                    {formatScore(summary.average_scores.content_quality)}/10
                  </span>
                </div>
                <Progress value={summary.average_scores.content_quality * 10} className="h-2" />
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Potencial de Engajamento</span>
                  <span className="text-sm text-muted-foreground">
                    {formatScore(summary.average_scores.engagement_potential)}/10
                  </span>
                </div>
                <Progress value={summary.average_scores.engagement_potential * 10} className="h-2" />
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Apelo Visual</span>
                  <span className="text-sm text-muted-foreground">
                    {formatScore(summary.average_scores.visual_appeal)}/10
                  </span>
                </div>
                <Progress value={summary.average_scores.visual_appeal * 10} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Feedback List */}
      {feedback.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhum feedback encontrado</h3>
            <p className="text-muted-foreground text-center mb-4">
              Conecte sua conta do Instagram para começar a receber feedback automático dos seus posts.
            </p>
            <Button>Conectar Instagram</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Feedback Recente</h2>
          
          <div className="grid grid-cols-1 gap-6">
            {feedback.map((item) => (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <CardTitle className="text-lg flex items-center space-x-2">
                        <span>Post {item.post_type === 'image' ? '📷' : '🎥'}</span>
                        <Badge variant="outline">
                          {item.post_type === 'image' ? 'Imagem' : 
                           item.post_type === 'video' ? 'Vídeo' : 'Carrossel'}
                        </Badge>
                      </CardTitle>
                      {item.post_caption && (
                        <CardDescription className="mt-2 line-clamp-2">
                          {item.post_caption}
                        </CardDescription>
                      )}
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getScoreColor(item.scores.overall)}`}>
                        {formatScore(item.scores.overall)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {getScoreLabel(item.scores.overall)}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Scores Breakdown */}
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <div className="text-lg font-semibold">
                          {formatScore(item.scores.content_quality)}
                        </div>
                        <div className="text-xs text-muted-foreground">Conteúdo</div>
                      </div>
                      <div>
                        <div className="text-lg font-semibold">
                          {formatScore(item.scores.engagement_potential)}
                        </div>
                        <div className="text-xs text-muted-foreground">Engajamento</div>
                      </div>
                      <div>
                        <div className="text-lg font-semibold">
                          {formatScore(item.scores.visual_appeal)}
                        </div>
                        <div className="text-xs text-muted-foreground">Visual</div>
                      </div>
                    </div>

                    {/* Feedback Text */}
                    <div className="bg-muted p-4 rounded-lg">
                      <h4 className="font-semibold mb-2">Feedback da IA:</h4>
                      <p className="text-sm">{item.feedback_text}</p>
                    </div>

                    {/* Suggestions */}
                    {item.suggestions && item.suggestions.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Sugestões de Melhoria:</h4>
                        <ul className="space-y-1">
                          {item.suggestions.map((suggestion, index) => (
                            <li key={index} className="text-sm flex items-start">
                              <span className="text-primary mr-2">•</span>
                              {suggestion}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex justify-between items-center pt-2 border-t">
                      <div className="text-xs text-muted-foreground">
                        Analisado em {new Date(item.created_at).toLocaleDateString('pt-BR')}
                      </div>
                      <Button variant="outline" size="sm" asChild>
                        <a href={item.post_url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="mr-2 h-4 w-4" />
                          Ver Post
                        </a>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Feedback;

