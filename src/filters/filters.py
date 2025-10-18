#!/usr/bin/env python3
"""
Sistema de Filtros Interativos para CNPJ
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class CNPJFilters:
    """Classe para gerenciar filtros interativos do sistema CNPJ"""
    
    def __init__(self):
        self.filters = {}
    
    def get_cnae_codes(self) -> Optional[List[str]]:
        """Solicita códigos CNAE do usuário"""
        print("\n📋 FILTRO: Códigos CNAE")
        print("Digite os códigos CNAE separados por vírgula (ex: 4781400,4782201)")
        print("Ou pressione Enter para pular este filtro")
        
        cnae_input = input("CNAE codes: ").strip()
        
        if not cnae_input:
            return None
        
        # Valida e limpa os códigos
        cnae_codes = [code.strip() for code in cnae_input.split(',') if code.strip()]
        
        if cnae_codes:
            print(f"✅ Filtro CNAE aplicado: {len(cnae_codes)} códigos")
            return cnae_codes
        
        return None
    
    def get_uf(self) -> Optional[str]:
        """Solicita UF do usuário"""
        print("\n🌍 FILTRO: Unidade Federativa (UF)")
        print("Digite a sigla da UF (ex: SP, RJ, MG)")
        print("Ou pressione Enter para pular este filtro")
        
        uf = input("UF: ").strip().upper()
        
        if uf and len(uf) == 2:
            print(f"✅ Filtro UF aplicado: {uf}")
            return uf
        elif uf:
            print("❌ UF inválida. Use sigla de 2 letras (ex: SP)")
            return self.get_uf()
        
        return None
    
    def get_codigo_municipio(self) -> Optional[str]:
        """Solicita código do município do usuário"""
        print("\n🏙️ FILTRO: Código do Município")
        print("Digite o código do município (ex: 9733)")
        print("Ou pressione Enter para pular este filtro")
        
        codigo = input("Código do município: ").strip()
        
        if codigo and codigo.isdigit():
            print(f"✅ Filtro município aplicado: {codigo}")
            return codigo
        elif codigo:
            print("❌ Código inválido. Use apenas números")
            return self.get_codigo_municipio()
        
        return None
    
    def get_situacao_cadastral(self) -> Optional[str]:
        """Solicita situação cadastral do usuário"""
        print("\n📊 FILTRO: Situação Cadastral")
        print("1 - Ativos (situação = 2) [PADRÃO]")
        print("2 - Inaptos (situação = 4)")
        print("3 - Inativos (situações = 1, 3, 8)")
        print("Ou pressione Enter para usar o padrão (Ativos)")
        
        opcao = input("Situação cadastral: ").strip()
        
        if opcao == '1' or opcao == '':
            print("✅ Filtro aplicado: Apenas empresas ATIVAS")
            return 'ativos'
        elif opcao == '2':
            print("✅ Filtro aplicado: Apenas empresas INAPTAS")
            return 'inaptos'
        elif opcao == '3':
            print("✅ Filtro aplicado: Apenas empresas INATIVAS")
            return 'inativos'
        else:
            print("❌ Opção inválida. Use 1, 2 ou 3")
            return self.get_situacao_cadastral()
        
        return None
    
    def get_data_inicio_atividade(self) -> Optional[Dict[str, str]]:
        """Solicita intervalo de data de início de atividade"""
        print("\n📅 FILTRO: Data de Início de Atividade (Intervalo)")
        print("Formato: YYYYMMDD (ex: 20200101)")
        print("Ou pressione Enter para pular este filtro")
        
        data_inicio = input("Data início (desde): ").strip()
        data_fim = input("Data fim (até): ").strip()
        
        if not data_inicio and not data_fim:
            return None
        
        # Validar formato das datas
        if data_inicio and not self._validar_data(data_inicio):
            print("❌ Data início inválida. Use formato YYYYMMDD")
            return self.get_data_inicio_atividade()
        
        if data_fim and not self._validar_data(data_fim):
            print("❌ Data fim inválida. Use formato YYYYMMDD")
            return self.get_data_inicio_atividade()
        
        if data_inicio and data_fim and data_inicio > data_fim:
            print("❌ Data início deve ser anterior à data fim")
            return self.get_data_inicio_atividade()
        
        filtro = {}
        if data_inicio:
            filtro['inicio'] = data_inicio
        if data_fim:
            filtro['fim'] = data_fim
        
        print(f"✅ Filtro data aplicado: {filtro}")
        return filtro
    
    def get_com_email(self) -> Optional[bool]:
        """Solicita se deve filtrar por registros com email"""
        print("\n📧 FILTRO: Registros com Email")
        print("s - Apenas registros COM email")
        print("n - Apenas registros SEM email")
        print("Ou pressione Enter para pular este filtro")
        
        opcao = input("Com email (s/n): ").strip().lower()
        
        if opcao == 's':
            print("✅ Filtro aplicado: Apenas registros COM email")
            return True
        elif opcao == 'n':
            print("✅ Filtro aplicado: Apenas registros SEM email")
            return False
        elif opcao:
            print("❌ Opção inválida. Use 's' ou 'n'")
            return self.get_com_email()
        
        return None
    
    def get_com_telefone(self) -> Optional[bool]:
        """Solicita se deve filtrar por registros com telefone"""
        print("\n📞 FILTRO: Registros com Telefone")
        print("s - Apenas registros COM telefone")
        print("n - Apenas registros SEM telefone")
        print("Ou pressione Enter para pular este filtro")
        
        opcao = input("Com telefone (s/n): ").strip().lower()
        
        if opcao == 's':
            print("✅ Filtro aplicado: Apenas registros COM telefone")
            return True
        elif opcao == 'n':
            print("✅ Filtro aplicado: Apenas registros SEM telefone")
            return False
        elif opcao:
            print("❌ Opção inválida. Use 's' ou 'n'")
            return self.get_com_telefone()
        
        return None
    
    def get_tipo_telefone(self) -> Optional[str]:
        """Solicita tipo de telefone"""
        print("\n📱 FILTRO: Tipo de Telefone")
        print("1 - Apenas fixos")
        print("2 - Apenas celulares")
        print("3 - Ambos (fixos e celulares)")
        print("Ou pressione Enter para pular este filtro")
        
        opcao = input("Tipo de telefone: ").strip()
        
        if opcao == '1':
            print("✅ Filtro aplicado: Apenas telefones fixos")
            return 'fixo'
        elif opcao == '2':
            print("✅ Filtro aplicado: Apenas celulares")
            return 'celular'
        elif opcao == '3':
            print("✅ Filtro aplicado: Ambos os tipos")
            return 'ambos'
        elif opcao:
            print("❌ Opção inválida. Use 1, 2 ou 3")
            return self.get_tipo_telefone()
        
        return None
    
    def get_opcao_tributaria(self) -> Optional[str]:
        """Solicita opção tributária"""
        print("\n💰 FILTRO: Opção Tributária")
        print("1 - Apenas MEI")
        print("2 - Sem MEI")
        print("3 - Todas")
        print("Ou pressione Enter para pular este filtro")
        
        opcao = input("Opção tributária: ").strip()
        
        if opcao == '1':
            print("✅ Filtro aplicado: Apenas MEI")
            return 'mei'
        elif opcao == '2':
            print("✅ Filtro aplicado: Sem MEI")
            return 'sem_mei'
        elif opcao == '3':
            print("✅ Filtro aplicado: Todas as opções")
            return 'todas'
        elif opcao:
            print("❌ Opção inválida. Use 1, 2 ou 3")
            return self.get_opcao_tributaria()
        
        return None
    
    def get_capital_social(self) -> Optional[str]:
        """Solicita faixa de capital social"""
        print("\n💵 FILTRO: Capital Social")
        print("1 - Maior que R$ 10.000")
        print("2 - Maior que R$ 50.000")
        print("3 - Maior que R$ 100.000")
        print("4 - Qualquer valor")
        print("Ou pressione Enter para pular este filtro")
        
        opcao = input("Faixa de capital: ").strip()
        
        if opcao == '1':
            print("✅ Filtro aplicado: Capital > R$ 10.000")
            return '10k'
        elif opcao == '2':
            print("✅ Filtro aplicado: Capital > R$ 50.000")
            return '50k'
        elif opcao == '3':
            print("✅ Filtro aplicado: Capital > R$ 100.000")
            return '100k'
        elif opcao == '4':
            print("✅ Filtro aplicado: Qualquer capital")
            return 'qualquer'
        elif opcao:
            print("❌ Opção inválida. Use 1, 2, 3 ou 4")
            return self.get_capital_social()
        
        return None
    
    def _validar_data(self, data: str) -> bool:
        """Valida formato de data YYYYMMDD"""
        if len(data) != 8 or not data.isdigit():
            return False
        
        try:
            datetime.strptime(data, '%Y%m%d')
            return True
        except ValueError:
            return False
    
    def coletar_filtros(self) -> Dict[str, Any]:
        """Coleta todos os filtros do usuário"""
        print("🔍 CONFIGURAÇÃO DE FILTROS")
        print("=" * 50)
        print("Configure os filtros de pesquisa ou pressione Enter para pular")
        
        filtros = {}
        
        # CNAE Codes
        cnae_codes = self.get_cnae_codes()
        if cnae_codes:
            filtros['cnae_codes'] = cnae_codes
        
        # UF
        uf = self.get_uf()
        if uf:
            filtros['uf'] = uf
        
        # Código do Município
        codigo_municipio = self.get_codigo_municipio()
        if codigo_municipio:
            filtros['codigo_municipio'] = codigo_municipio
        
        # Situação Cadastral
        situacao = self.get_situacao_cadastral()
        if situacao:
            filtros['situacao_cadastral'] = situacao
        
        # Data de Início de Atividade
        data_filtro = self.get_data_inicio_atividade()
        if data_filtro:
            filtros['data_inicio_atividade'] = data_filtro
        
        # Com Email
        com_email = self.get_com_email()
        if com_email is not None:
            filtros['com_email'] = com_email
        
        # Com Telefone
        com_telefone = self.get_com_telefone()
        if com_telefone is not None:
            filtros['com_telefone'] = com_telefone
        
        # Tipo de Telefone
        tipo_telefone = self.get_tipo_telefone()
        if tipo_telefone:
            filtros['tipo_telefone'] = tipo_telefone
        
        # Opção Tributária
        opcao_tributaria = self.get_opcao_tributaria()
        if opcao_tributaria:
            filtros['opcao_tributaria'] = opcao_tributaria
        
        # Capital Social
        capital_social = self.get_capital_social()
        if capital_social:
            filtros['capital_social'] = capital_social
        
        print("\n" + "=" * 50)
        if filtros:
            print("✅ FILTROS CONFIGURADOS:")
            for chave, valor in filtros.items():
                print(f"   {chave}: {valor}")
        else:
            print("ℹ️ Nenhum filtro aplicado - processando todos os registros")
        
        return filtros
