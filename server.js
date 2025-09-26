const express = require('express');
const cors = require('cors');

const app = express();

// Configurar CORS para permitir requisições de http://localhost:3000
app.use(cors({ origin: 'http://localhost:3000' }));

// Middleware para parsear JSON (se necessário)
app.use(express.json());

// Rota de exemplo para /users/me
app.get('/users/me', (req, res) => {
  // Lógica para retornar os dados do usuário
  // Substitua isso pela sua lógica real de autenticação
  if (!req.headers.authorization) {
    return res.status(401).json({ message: 'Token não fornecido' });
  }
  // Exemplo de resposta
  res.json({ message: 'Usuário encontrado', user: { id: 1, name: 'Exemplo' } });
});

// Iniciar o servidor
const PORT = 8001;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});