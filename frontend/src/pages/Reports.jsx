import React, { useState, useEffect } from 'react';
import { reportsAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { FileText, Download, Plus, Calendar, Clock, CheckCircle, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [generating, setGenerating] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  const [newReport, setNewReport] = useState({
    report_type: 'weekly',
    title: '',
    summary: '',
    period_start: '',
    period_end: '',
  });

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await reportsAPI.getReports();
      setReports(response.data);
    } catch (err) {
      console.error('Error fetching reports:', err);
      setError('Erro ao carregar relatórios');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (e) => {
    e.preventDefault();
    setGenerating(true);

    try {
      await reportsAPI.generateReport({
        ...newReport,
        period_start: new Date(newReport.period_start).toISOString(),
        period_end: new Date(newReport.period_end).toISOString(),
      });

      setDialogOpen(false);
      setNewReport({
        report_type: 'weekly',
        title: '',
        summary: '',
        period_start: '',
        period_end: '',
      });
      
      // Refresh reports list
      fetchReports();
    } catch (err) {
      console.error('Error generating report:', err);
      setError('Erro ao gerar relatório');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (reportId) => {
    try {
      const response = await reportsAPI.downloadReport(reportId);
      
      // Create blob and download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `report_${reportId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading report:', err);
      setError('Erro ao baixar relatório');
    }
  };

  const getReportTypeLabel = (type) => {
    const types = {
      weekly: 'Semanal',
      monthly: 'Mensal',
      custom: 'Personalizado',
    };
    return types[type] || type;
  };

  const getStatusBadge = (report) => {
    if (report.is_ready) {
      return <Badge variant="default" className="bg-green-100 text-green-800">Pronto</Badge>;
    }
    return <Badge variant="secondary">Processando</Badge>;
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Relatórios</h1>
          <p className="text-muted-foreground">
            Gere e baixe relatórios detalhados da sua performance
          </p>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Gerar Relatório
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Gerar Novo Relatório</DialogTitle>
              <DialogDescription>
                Configure os parâmetros do seu relatório
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleGenerateReport} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="report_type">Tipo de Relatório</Label>
                <Select
                  value={newReport.report_type}
                  onValueChange={(value) => setNewReport({ ...newReport, report_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="weekly">Semanal</SelectItem>
                    <SelectItem value="monthly">Mensal</SelectItem>
                    <SelectItem value="custom">Personalizado</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="title">Título</Label>
                <Input
                  id="title"
                  value={newReport.title}
                  onChange={(e) => setNewReport({ ...newReport, title: e.target.value })}
                  placeholder="Ex: Relatório Semanal - Janeiro 2024"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="summary">Resumo</Label>
                <Input
                  id="summary"
                  value={newReport.summary}
                  onChange={(e) => setNewReport({ ...newReport, summary: e.target.value })}
                  placeholder="Breve descrição do relatório"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="period_start">Data Início</Label>
                  <Input
                    id="period_start"
                    type="date"
                    value={newReport.period_start}
                    onChange={(e) => setNewReport({ ...newReport, period_start: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="period_end">Data Fim</Label>
                  <Input
                    id="period_end"
                    type="date"
                    value={newReport.period_end}
                    onChange={(e) => setNewReport({ ...newReport, period_end: e.target.value })}
                    required
                  />
                </div>
              </div>

              <Button type="submit" disabled={generating} className="w-full">
                {generating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Gerando...
                  </>
                ) : (
                  'Gerar Relatório'
                )}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Reports List */}
      {reports.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhum relatório encontrado</h3>
            <p className="text-muted-foreground text-center mb-4">
              Você ainda não gerou nenhum relatório. Clique no botão acima para criar seu primeiro relatório.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reports.map((report) => (
            <Card key={report.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{report.title}</CardTitle>
                    <CardDescription className="mt-1">
                      {report.summary}
                    </CardDescription>
                  </div>
                  {getStatusBadge(report)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Calendar className="mr-2 h-4 w-4" />
                    <span>
                      {format(new Date(report.period_start), 'dd/MM/yyyy', { locale: ptBR })} - {' '}
                      {format(new Date(report.period_end), 'dd/MM/yyyy', { locale: ptBR })}
                    </span>
                  </div>
                  
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="mr-2 h-4 w-4" />
                    <span>
                      Criado em {format(new Date(report.created_at), 'dd/MM/yyyy HH:mm', { locale: ptBR })}
                    </span>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <Badge variant="outline">
                      {getReportTypeLabel(report.report_type)}
                    </Badge>
                    
                    {report.is_ready ? (
                      <Button
                        size="sm"
                        onClick={() => handleDownload(report.id)}
                        className="flex items-center"
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Baixar
                      </Button>
                    ) : (
                      <Button size="sm" disabled>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processando
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Relatórios Automáticos</CardTitle>
          <CardDescription>
            Configure relatórios para serem gerados automaticamente
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border border-border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">Relatório Semanal</h3>
                <Badge variant="outline">Inativo</Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Receba um relatório semanal toda segunda-feira
              </p>
              <Button variant="outline" size="sm">
                Ativar
              </Button>
            </div>
            
            <div className="p-4 border border-border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">Relatório Mensal</h3>
                <Badge variant="outline">Inativo</Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Receba um relatório mensal no primeiro dia do mês
              </p>
              <Button variant="outline" size="sm">
                Ativar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;

