"""
Sistema de Banco de Dados PostgreSQL - IASenior
Gerencia persistência de dados históricos, eventos, métricas e alertas.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_values
    from psycopg2.pool import ThreadedConnectionPool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 não instalado. Instale com: pip install psycopg2-binary")

from config import BASE_DIR

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Gerenciador de banco de dados PostgreSQL para o sistema IASenior.
    Gerencia conexões, schema e operações de persistência.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            config: Configurações de conexão (dbname, user, password, host, port)
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 não está instalado. Instale com: pip install psycopg2-binary")
        
        self.config = config or {}
        self.connection_pool = None
        self._initialize_connection()
        self._create_schema()
    
    def _initialize_connection(self):
        """Inicializa pool de conexões PostgreSQL."""
        try:
            # Configurações de conexão
            db_config = {
                'dbname': self.config.get('dbname', os.getenv('DB_NAME', 'iasenior')),
                'user': self.config.get('user', os.getenv('DB_USER', 'iasenior')),
                'password': self.config.get('password', os.getenv('DB_PASSWORD', 'iasenior')),
                'host': self.config.get('host', os.getenv('DB_HOST', 'localhost')),
                'port': self.config.get('port', int(os.getenv('DB_PORT', '5432')))
            }
            
            # Criar pool de conexões
            self.connection_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **db_config
            )
            
            logger.info(f"✅ Pool de conexões PostgreSQL criado: {db_config['dbname']}@{db_config['host']}:{db_config['port']}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao PostgreSQL: {e}")
            raise
    
    def get_connection(self):
        """Obtém uma conexão do pool."""
        if not self.connection_pool:
            self._initialize_connection()
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Retorna conexão ao pool."""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def _create_schema(self):
        """Cria schema do banco de dados se não existir."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Tabela de eventos
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS eventos (
                        id SERIAL PRIMARY KEY,
                        tipo VARCHAR(50) NOT NULL,
                        mensagem TEXT NOT NULL,
                        severidade VARCHAR(20) NOT NULL DEFAULT 'info',
                        metadata JSONB,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Índices para eventos
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(tipo);
                    CREATE INDEX IF NOT EXISTS idx_eventos_timestamp ON eventos(timestamp);
                    CREATE INDEX IF NOT EXISTS idx_eventos_severidade ON eventos(severidade);
                """)
                
                # Tabela de métricas
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS metricas (
                        id SERIAL PRIMARY KEY,
                        tipo_metrica VARCHAR(50) NOT NULL,
                        valor NUMERIC NOT NULL,
                        unidade VARCHAR(20),
                        metadata JSONB,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Índices para métricas
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_metricas_tipo ON metricas(tipo_metrica);
                    CREATE INDEX IF NOT EXISTS idx_metricas_timestamp ON metricas(timestamp);
                """)
                
                # Tabela de alertas
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS alertas (
                        id SERIAL PRIMARY KEY,
                        tipo_alerta VARCHAR(50) NOT NULL,
                        titulo VARCHAR(200) NOT NULL,
                        mensagem TEXT NOT NULL,
                        severidade VARCHAR(20) NOT NULL DEFAULT 'warning',
                        status VARCHAR(20) NOT NULL DEFAULT 'ativo',
                        metadata JSONB,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        resolvido_em TIMESTAMP,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Índices para alertas
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_alertas_tipo ON alertas(tipo_alerta);
                    CREATE INDEX IF NOT EXISTS idx_alertas_status ON alertas(status);
                    CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas(timestamp);
                """)
                
                # Tabela de histórico de ocupação
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS historico_ocupacao (
                        id SERIAL PRIMARY KEY,
                        area VARCHAR(50) NOT NULL,
                        quantidade INTEGER NOT NULL,
                        metadata JSONB,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Índices para histórico de ocupação
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_ocupacao_area ON historico_ocupacao(area);
                    CREATE INDEX IF NOT EXISTS idx_ocupacao_timestamp ON historico_ocupacao(timestamp);
                """)
                
                # Tabela de detecções de queda
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS deteccoes_queda (
                        id SERIAL PRIMARY KEY,
                        confianca NUMERIC,
                        posicao_x NUMERIC,
                        posicao_y NUMERIC,
                        metadata JSONB,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Índice para detecções de queda
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_queda_timestamp ON deteccoes_queda(timestamp);
                """)
                
                # Tabela de monitoramento de banheiro
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS monitoramento_banheiro (
                        id SERIAL PRIMARY KEY,
                        track_id VARCHAR(50),
                        tempo_segundos INTEGER NOT NULL,
                        alerta BOOLEAN NOT NULL DEFAULT FALSE,
                        metadata JSONB,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Índice para monitoramento de banheiro
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_banheiro_timestamp ON monitoramento_banheiro(timestamp);
                    CREATE INDEX IF NOT EXISTS idx_banheiro_alerta ON monitoramento_banheiro(alerta);
                """)
                
                # Tabela de níveis de acesso (roles)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS niveis_acesso (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(50) UNIQUE NOT NULL,
                        descricao TEXT,
                        nivel INTEGER NOT NULL UNIQUE,
                        permissoes JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Tabela de usuários
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE,
                        senha_hash VARCHAR(255) NOT NULL,
                        nome_completo VARCHAR(255),
                        nivel_acesso_id INTEGER REFERENCES niveis_acesso(id) ON DELETE RESTRICT,
                        ativo BOOLEAN NOT NULL DEFAULT TRUE,
                        ultimo_login TIMESTAMP,
                        tentativas_login_falhadas INTEGER DEFAULT 0,
                        bloqueado_ate TIMESTAMP,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Tabela de sessões
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sessoes (
                        id SERIAL PRIMARY KEY,
                        usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                        token VARCHAR(255) UNIQUE NOT NULL,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        expira_em TIMESTAMP NOT NULL,
                        ativo BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Tabela de logs de autenticação
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS logs_autenticacao (
                        id SERIAL PRIMARY KEY,
                        usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
                        username VARCHAR(100),
                        tipo_evento VARCHAR(50) NOT NULL,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        sucesso BOOLEAN NOT NULL,
                        mensagem TEXT,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Índices para autenticação
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
                    CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
                    CREATE INDEX IF NOT EXISTS idx_usuarios_nivel_acesso ON usuarios(nivel_acesso_id);
                    CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON usuarios(ativo);
                    CREATE INDEX IF NOT EXISTS idx_sessoes_token ON sessoes(token);
                    CREATE INDEX IF NOT EXISTS idx_sessoes_usuario ON sessoes(usuario_id);
                    CREATE INDEX IF NOT EXISTS idx_sessoes_ativo ON sessoes(ativo);
                    CREATE INDEX IF NOT EXISTS idx_sessoes_expira_em ON sessoes(expira_em);
                    CREATE INDEX IF NOT EXISTS idx_logs_auth_usuario ON logs_autenticacao(usuario_id);
                    CREATE INDEX IF NOT EXISTS idx_logs_auth_timestamp ON logs_autenticacao(timestamp);
                    CREATE INDEX IF NOT EXISTS idx_logs_auth_tipo ON logs_autenticacao(tipo_evento);
                """)
                
                # Inserir níveis de acesso padrão
                cur.execute("""
                    INSERT INTO niveis_acesso (nome, descricao, nivel, permissoes)
                    VALUES 
                        ('admin', 'Administrador com acesso total ao sistema', 1, '{"acesso_total": true, "gerenciar_usuarios": true, "configurar_sistema": true, "visualizar_dados": true, "editar_dados": true}'::jsonb),
                        ('operador', 'Operador com acesso a operações e visualização', 2, '{"visualizar_dados": true, "editar_dados": true, "gerenciar_alertas": true}'::jsonb),
                        ('visualizador', 'Apenas visualização de dados e relatórios', 3, '{"visualizar_dados": true}'::jsonb),
                        ('cliente', 'Cliente com acesso limitado ao portal', 4, '{"visualizar_portal": true, "visualizar_relatorios": true}'::jsonb)
                    ON CONFLICT (nome) DO NOTHING;
                """)
                
                conn.commit()
                logger.info("✅ Schema do banco de dados criado/verificado com sucesso")
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao criar schema: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def inserir_evento(self, tipo: str, mensagem: str, severidade: str = 'info', metadata: Dict = None) -> int:
        """
        Insere um evento no banco de dados.
        
        Args:
            tipo: Tipo do evento (ex: 'queda', 'alerta_banheiro', 'captura')
            mensagem: Mensagem do evento
            severidade: Severidade ('info', 'warning', 'error')
            metadata: Dados adicionais em formato JSON
        
        Returns:
            ID do evento inserido
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO eventos (tipo, mensagem, severidade, metadata, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (tipo, mensagem, severidade, json.dumps(metadata) if metadata else None, datetime.now()))
                
                evento_id = cur.fetchone()[0]
                conn.commit()
                return evento_id
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao inserir evento: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def inserir_metrica(self, tipo_metrica: str, valor: float, unidade: str = None, metadata: Dict = None) -> int:
        """
        Insere uma métrica no banco de dados.
        
        Args:
            tipo_metrica: Tipo da métrica (ex: 'pessoas_quarto', 'fps', 'latencia')
            valor: Valor da métrica
            unidade: Unidade da métrica (ex: 'pessoas', 'fps', 'ms')
            metadata: Dados adicionais
        
        Returns:
            ID da métrica inserida
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO metricas (tipo_metrica, valor, unidade, metadata, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (tipo_metrica, valor, unidade, json.dumps(metadata) if metadata else None, datetime.now()))
                
                metrica_id = cur.fetchone()[0]
                conn.commit()
                return metrica_id
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao inserir métrica: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def inserir_alerta(self, tipo_alerta: str, titulo: str, mensagem: str, 
                      severidade: str = 'warning', metadata: Dict = None) -> int:
        """
        Insere um alerta no banco de dados.
        
        Args:
            tipo_alerta: Tipo do alerta (ex: 'banheiro_tempo', 'queda', 'sistema')
            titulo: Título do alerta
            mensagem: Mensagem do alerta
            severidade: Severidade ('info', 'warning', 'error', 'critical')
            metadata: Dados adicionais
        
        Returns:
            ID do alerta inserido
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO alertas (tipo_alerta, titulo, mensagem, severidade, metadata, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (tipo_alerta, titulo, mensagem, severidade, 
                      json.dumps(metadata) if metadata else None, datetime.now()))
                
                alerta_id = cur.fetchone()[0]
                conn.commit()
                return alerta_id
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao inserir alerta: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def inserir_ocupacao(self, area: str, quantidade: int, metadata: Dict = None) -> int:
        """
        Insere registro de ocupação (quarto, banheiro, etc).
        
        Args:
            area: Área monitorada ('quarto', 'banheiro')
            quantidade: Quantidade de pessoas
            metadata: Dados adicionais
        
        Returns:
            ID do registro inserido
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO historico_ocupacao (area, quantidade, metadata, timestamp)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (area, quantidade, json.dumps(metadata) if metadata else None, datetime.now()))
                
                registro_id = cur.fetchone()[0]
                conn.commit()
                return registro_id
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao inserir ocupação: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def inserir_deteccao_queda(self, confianca: float = None, posicao_x: float = None, 
                               posicao_y: float = None, metadata: Dict = None) -> int:
        """
        Insere detecção de queda.
        
        Args:
            confianca: Confiança da detecção
            posicao_x: Posição X
            posicao_y: Posição Y
            metadata: Dados adicionais
        
        Returns:
            ID da detecção inserida
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO deteccoes_queda (confianca, posicao_x, posicao_y, metadata, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (confianca, posicao_x, posicao_y, 
                      json.dumps(metadata) if metadata else None, datetime.now()))
                
                deteccao_id = cur.fetchone()[0]
                conn.commit()
                return deteccao_id
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao inserir detecção de queda: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def obter_eventos(self, tipo: str = None, severidade: str = None, 
                     inicio: datetime = None, fim: datetime = None, limite: int = 100) -> List[Dict]:
        """
        Obtém eventos do banco de dados.
        
        Args:
            tipo: Filtrar por tipo
            severidade: Filtrar por severidade
            inicio: Data/hora inicial
            fim: Data/hora final
            limite: Limite de resultados
        
        Returns:
            Lista de eventos
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM eventos WHERE 1=1"
                params = []
                
                if tipo:
                    query += " AND tipo = %s"
                    params.append(tipo)
                
                if severidade:
                    query += " AND severidade = %s"
                    params.append(severidade)
                
                if inicio:
                    query += " AND timestamp >= %s"
                    params.append(inicio)
                
                if fim:
                    query += " AND timestamp <= %s"
                    params.append(fim)
                
                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limite)
                
                cur.execute(query, params)
                eventos = cur.fetchall()
                
                # Converter para dict simples
                return [dict(evento) for evento in eventos]
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter eventos: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def obter_metricas(self, tipo_metrica: str = None, inicio: datetime = None, 
                      fim: datetime = None, limite: int = 1000) -> List[Dict]:
        """
        Obtém métricas do banco de dados.
        
        Args:
            tipo_metrica: Filtrar por tipo
            inicio: Data/hora inicial
            fim: Data/hora final
            limite: Limite de resultados
        
        Returns:
            Lista de métricas
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM metricas WHERE 1=1"
                params = []
                
                if tipo_metrica:
                    query += " AND tipo_metrica = %s"
                    params.append(tipo_metrica)
                
                if inicio:
                    query += " AND timestamp >= %s"
                    params.append(inicio)
                
                if fim:
                    query += " AND timestamp <= %s"
                    params.append(fim)
                
                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limite)
                
                cur.execute(query, params)
                metricas = cur.fetchall()
                
                return [dict(metrica) for metrica in metricas]
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter métricas: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def obter_alertas_ativos(self) -> List[Dict]:
        """Obtém alertas ativos."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM alertas 
                    WHERE status = 'ativo'
                    ORDER BY timestamp DESC
                """)
                alertas = cur.fetchall()
                return [dict(alerta) for alerta in alertas]
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter alertas ativos: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def resolver_alerta(self, alerta_id: int):
        """Marca um alerta como resolvido."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE alertas 
                    SET status = 'resolvido', resolvido_em = %s
                    WHERE id = %s
                """, (datetime.now(), alerta_id))
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao resolver alerta: {e}")
        finally:
            self.return_connection(conn)
    
    def obter_estatisticas_ocupacao(self, area: str, inicio: datetime = None, 
                                   fim: datetime = None) -> Dict:
        """
        Obtém estatísticas de ocupação de uma área.
        
        Returns:
            Dict com média, máximo, mínimo, total de registros
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        AVG(quantidade) as media,
                        MAX(quantidade) as maximo,
                        MIN(quantidade) as minimo,
                        COUNT(*) as total_registros
                    FROM historico_ocupacao
                    WHERE area = %s
                """
                params = [area]
                
                if inicio:
                    query += " AND timestamp >= %s"
                    params.append(inicio)
                
                if fim:
                    query += " AND timestamp <= %s"
                    params.append(fim)
                
                cur.execute(query, params)
                resultado = cur.fetchone()
                
                if resultado:
                    return dict(resultado)
                return {'media': 0, 'maximo': 0, 'minimo': 0, 'total_registros': 0}
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {'media': 0, 'maximo': 0, 'minimo': 0, 'total_registros': 0}
        finally:
            self.return_connection(conn)
    
    def fechar(self):
        """Fecha o pool de conexões."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✅ Pool de conexões fechado")
    
    # ==================== MÉTODOS DE AUTENTICAÇÃO ====================
    
    def criar_usuario(self, username: str, senha_hash: str, email: str = None, 
                     nome_completo: str = None, nivel_acesso_id: int = 4, 
                     metadata: Dict = None) -> int:
        """
        Cria um novo usuário no banco de dados.
        
        Args:
            username: Nome de usuário único
            senha_hash: Hash da senha (bcrypt)
            email: Email do usuário
            nome_completo: Nome completo
            nivel_acesso_id: ID do nível de acesso (1=admin, 2=operador, 3=visualizador, 4=cliente)
            metadata: Dados adicionais
        
        Returns:
            ID do usuário criado
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO usuarios (username, email, senha_hash, nome_completo, nivel_acesso_id, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (username, email, senha_hash, nome_completo, nivel_acesso_id, 
                      json.dumps(metadata) if metadata else None))
                
                usuario_id = cur.fetchone()[0]
                conn.commit()
                logger.info(f"✅ Usuário {username} criado com ID: {usuario_id}")
                return usuario_id
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao criar usuário: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def obter_usuario_por_username(self, username: str) -> Optional[Dict]:
        """Obtém usuário por username."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT u.*, na.nome as nivel_nome, na.nivel as nivel_numero, na.permissoes
                    FROM usuarios u
                    JOIN niveis_acesso na ON u.nivel_acesso_id = na.id
                    WHERE u.username = %s
                """, (username,))
                
                usuario = cur.fetchone()
                return dict(usuario) if usuario else None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter usuário: {e}")
            return None
        finally:
            self.return_connection(conn)
    
    def obter_usuario_por_id(self, usuario_id: int) -> Optional[Dict]:
        """Obtém usuário por ID."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT u.*, na.nome as nivel_nome, na.nivel as nivel_numero, na.permissoes
                    FROM usuarios u
                    JOIN niveis_acesso na ON u.nivel_acesso_id = na.id
                    WHERE u.id = %s
                """, (usuario_id,))
                
                usuario = cur.fetchone()
                return dict(usuario) if usuario else None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter usuário: {e}")
            return None
        finally:
            self.return_connection(conn)
    
    def atualizar_ultimo_login(self, usuario_id: int):
        """Atualiza último login do usuário."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE usuarios 
                    SET ultimo_login = %s, tentativas_login_falhadas = 0
                    WHERE id = %s
                """, (datetime.now(), usuario_id))
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao atualizar último login: {e}")
        finally:
            self.return_connection(conn)
    
    def incrementar_tentativas_falhadas(self, username: str):
        """Incrementa tentativas de login falhadas."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE usuarios 
                    SET tentativas_login_falhadas = tentativas_login_falhadas + 1,
                        bloqueado_ate = CASE 
                            WHEN tentativas_login_falhadas >= 4 THEN CURRENT_TIMESTAMP + INTERVAL '30 minutes'
                            ELSE bloqueado_ate
                        END
                    WHERE username = %s
                """, (username,))
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao incrementar tentativas: {e}")
        finally:
            self.return_connection(conn)
    
    def criar_sessao(self, usuario_id: int, token: str, ip_address: str = None, 
                     user_agent: str = None, expira_em: datetime = None) -> int:
        """Cria uma nova sessão de usuário."""
        if expira_em is None:
            expira_em = datetime.now() + timedelta(hours=24)
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sessoes (usuario_id, token, ip_address, user_agent, expira_em)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (usuario_id, token, ip_address, user_agent, expira_em))
                
                sessao_id = cur.fetchone()[0]
                conn.commit()
                return sessao_id
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao criar sessão: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def obter_sessao(self, token: str) -> Optional[Dict]:
        """Obtém sessão por token."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.*, u.username, u.nivel_acesso_id, u.ativo as usuario_ativo
                    FROM sessoes s
                    JOIN usuarios u ON s.usuario_id = u.id
                    WHERE s.token = %s 
                    AND s.ativo = TRUE 
                    AND s.expira_em > CURRENT_TIMESTAMP
                """, (token,))
                
                sessao = cur.fetchone()
                return dict(sessao) if sessao else None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter sessão: {e}")
            return None
        finally:
            self.return_connection(conn)
    
    def invalidar_sessao(self, token: str):
        """Invalida uma sessão (logout)."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sessoes 
                    SET ativo = FALSE 
                    WHERE token = %s
                """, (token,))
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao invalidar sessão: {e}")
        finally:
            self.return_connection(conn)
    
    def invalidar_sessoes_usuario(self, usuario_id: int):
        """Invalida todas as sessões de um usuário."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sessoes 
                    SET ativo = FALSE 
                    WHERE usuario_id = %s
                """, (usuario_id,))
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao invalidar sessões: {e}")
        finally:
            self.return_connection(conn)
    
    def limpar_sessoes_expiradas(self):
        """Remove sessões expiradas."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sessoes 
                    SET ativo = FALSE 
                    WHERE expira_em < CURRENT_TIMESTAMP AND ativo = TRUE
                """)
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao limpar sessões: {e}")
        finally:
            self.return_connection(conn)
    
    def registrar_log_autenticacao(self, usuario_id: int = None, username: str = None,
                                  tipo_evento: str = 'login', ip_address: str = None,
                                  user_agent: str = None, sucesso: bool = True,
                                  mensagem: str = None, metadata: Dict = None):
        """Registra log de autenticação."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO logs_autenticacao 
                    (usuario_id, username, tipo_evento, ip_address, user_agent, sucesso, mensagem, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (usuario_id, username, tipo_evento, ip_address, user_agent, sucesso, mensagem,
                      json.dumps(metadata) if metadata else None))
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao registrar log: {e}")
        finally:
            self.return_connection(conn)
    
    def obter_niveis_acesso(self) -> List[Dict]:
        """Obtém todos os níveis de acesso."""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM niveis_acesso 
                    ORDER BY nivel ASC
                """)
                niveis = cur.fetchall()
                return [dict(nivel) for nivel in niveis]
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter níveis: {e}")
            return []
        finally:
            self.return_connection(conn)


# Instância global (singleton)
_db_manager = None


def get_db_manager(config: Dict[str, Any] = None) -> DatabaseManager:
    """
    Obtém instância global do gerenciador de banco de dados.
    
    Args:
        config: Configurações de conexão (opcional)
    
    Returns:
        Instância de DatabaseManager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(config)
    return _db_manager

