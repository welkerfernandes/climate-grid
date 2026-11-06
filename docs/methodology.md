# Metodologia e avaliação

Regras explicáveis: um limite excedido gera watch; dois ou mais geram high. Qualquer variável ausente gera unknown, mesmo se outras excederem limites. Não há previsão própria ou modelo treinado: a previsão meteorológica pertence ao provedor.

## Evidência disponível

Testes cobrem invariantes, entradas inválidas, isolamento, falhas da fonte e modo demonstrativo.
Não existem benchmarks de produção, acurácia preditiva alegada ou métricas de clientes.
Fixtures sintéticas não servem como validação de generalização.

## Limites

Dados em UTC, não no fuso local da unidade. Limites são heurísticas de demonstração e não constituem avaliação de segurança, alertas oficiais ou recomendação agronômica. O serviço não faz notificações nem monitora unidades automaticamente.
