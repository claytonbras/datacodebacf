#!/usr/bin/python

# Copyright 2019, Gurobi Optimization, LLC

# O Problema do Balanceamento de Currículo consiste em atribuir disciplinas a periodos de forma que a carga acadêmica
# de cada período seja balanceada o quanto for possível, respeitando relações de precedência(pre-requisitos) entre as
# disciplinas.
# O objetivo inicial é minimizar o maior valor dentre todos os valores de cargas dos períodos.
# Neste modelo, são adicionadas ainda dois objetivos: reduzir a possibilidade de, quanto maiores forem as retenções históricas
# das disciplinas, que estas não localizem-se em um mesmo período (realização de um melhor balanceio de dificuldades);
# e também diminuir a distância entre disciplinas relacionadas por meio do grau de relação entre estas.
# Assim, são definidas as variáveis (C) e (IR); e um somatório que representa o produto da relação entre as disciplinas e as distâncias entre as mesmas,
# influenciados pelas localizações das disciplinas ao longo dos períodos.

from gurobipy import *
from datetime import datetime
try:

    #Método que imprime a grade resultante
    def imprimirGrade(periodos, disciplinas, codigosDisciplinasTraducao, creditos, indicesRetencao, resultados):
        for j in periodos:
            carga = (sum(round(X[i][j].x) * creditos[i] for i in disciplinas))
            indiceRetencao = (sum(round(X[i][j].x) * indicesRetencao[i] for i in disciplinas))
            print("Período " + str(j) + " - Carga: " + str(carga) + " - Retenção " + str(indiceRetencao));
            print("\n")
            for i in disciplinas:
                if (round(X[i][j].x) == 1):
                    print(codigosDisciplinasTraducao[i], end=' ')
                    print(' - C: ' + str(creditos[i]) + ' - IR: ' + str(indicesRetencao[i]))
            print("\n")

        for j in periodos:
            carga = (sum(round(X[i][j].x) * creditos[i] for i in disciplinas))
            indiceRetencao = (sum(round(X[i][j].x) * indicesRetencao[i] for i in disciplinas))
            resultados.append("Período " + str(j) + " - Carga: " + str(carga) + " - Retenção " + str(indiceRetencao));
            resultados.append("\n")
            for i in disciplinas:
                if (int(round(X[i][j].x)) == 1):
                    resultados.append(str(codigosDisciplinasTraducao[i]))
                    resultados.append(' - C: ' + str(creditos[i]) + ' - IR: ' + str(indicesRetencao[i]))
                    resultados.append("\n")
            resultados.append("\n")
        resultados.append("\n")

    #Método que imprime a soma das cargas de cada período
    def imprimirSomatorioCargasPorPeriodo(periodos, creditos, disciplinas, resultados):

        print("CARGA PERÍODO")

        for j in periodos:
            carga = (sum(round(X[i][j].x) * creditos[i] for i in disciplinas))
            print("Carga Período " + str(j) + " = " + str(carga))

        resultados.append("CARGA PERÍODO")
        resultados.append('\n')
        for j in periodos:
            carga = (sum(round(X[i][j].x) * creditos[i] for i in disciplinas))
            resultados.append("Carga Período " + str(j) + " = " + str(carga))
            resultados.append('\n')
        resultados.append("\n")

    #Método que imprime a soma dos índices de retenção de cada período
    def imprimirSomatorioIndicesRetencao(periodos, indices_retencao, disciplinas, resultados):

        print("ÍNDICES RETENÇÃO")

        for j in periodos:
            indiceRetencao = (sum(round(X[i][j].x) * indices_retencao[i] for i in disciplinas))
            print("Índice retenção Período " + str(j) + " = " + str(indiceRetencao))

        resultados.append("ÍNDICES RETENÇÃO")
        resultados.append('\n')
        for j in periodos:
            indiceRetencao = (sum(round(X[i][j].x) * indices_retencao[i] for i in disciplinas))
            resultados.append("Índice retenção Período " + str(j) + " = " + str(indiceRetencao))
            resultados.append('\n')
        resultados.append("\n")

    #Método que imprime os valores das variáveis constantes no resultado da função objetivo
    def imprimirValoresVariaveis(resultados, C, IR, RD):
        print('VALORES RESULTANTES DAS VARIÁVEIS')
        print('Valor de C no resultado da função objetivo: %g' %C.X)
        print('Valor de IR no resultado da função objetivo: %g' %IR.X)
        print('Valor de RD no resultado da função objetivo: %g' %RD.getValue())

        resultados.append('VALORES RESULTANTES DAS VARIÁVEIS')
        resultados.append('\n')
        resultados.append('Valor de C no resultado da função objetivo: %g' %C.X)
        resultados.append('\n')
        resultados.append('Valor de IR no resultado da função objetivo: %g' %IR.X)
        resultados.append('\n')
        resultados.append('Valor de RD no resultado da função objetivo: %g' %RD.getValue())
        resultados.append('\n')
        resultados.append("\n")

    #Método que imprime os valores das variáveis constantes no resultado da função objetivo
    def imprimirPesos(resultados, pesoCarga, pesoRetencao, pesoRelacao):
        print("PESOS")
        print('Valor Peso Carga: %g' %pesoCarga)
        print('Valor Peso Retenção: %g' %pesoRetencao)
        print('Valor Peso Relação: %g' %pesoRelacao)

        resultados.append("PESOS")
        resultados.append("\n")
        resultados.append('Valor Peso Carga: %g' %pesoCarga)
        resultados.append("\n")
        resultados.append('Valor Peso Retenção: %g' %pesoRetencao)
        resultados.append("\n")
        resultados.append('Valor Peso Relação: %g' %pesoRelacao)
        resultados.append("\n")
        resultados.append("\n")

    #Método que imprime os valores das variáveis constantes no resultado da função objetivo
    def imprimirValoresParaFronteiraPareto(resultadosPareto, pesoCarga, pesoRetencao, pesoRelacao):
        print('Pareto: '+str(round(C.X))+';'+str(round(IR.X))+';'+str(round(RD.getValue()))+';'+str(pesoCarga)+';'+str(pesoRetencao)+';'+str(pesoRelacao))
        resultadosPareto.append(str(round(C.X))+';'+str(round(IR.X))+';'+str(round(RD.getValue()))+';'+str(pesoCarga)+';'+str(pesoRetencao)+';'+str(pesoRelacao))
        resultadosPareto.append('\n')

    resultados = list()
    resultadosPareto = list()

    # cria um novo modelo
    modelo = Model("curriculumbalancing")
    modelo.setParam('OutputFlag', False) # turns off solver chatter

    #dicionário que referenciam os nomes das disciplinas nas instancias
    codigosDisciplinasTraducao = {
        0: ['MAT001', 'FUNDAMENTOS DE MATEMÁTICA'], 1: ['MAT007', 'INTRODUÇÃO À LOGICA COMPUTACIONAL'],
        2: ['COM040', 'FUNDAMENTOS DE SISTEMAS DE INFORMAÇÃO'], 3: ['MAT006', 'MATEMÁTICA DISCRETA'],
        4: ['COM043', 'INGLÊS INSTRUMENTAL'], 5: ['COM001', 'ALGORITMOS E ESTRUTURA DE DADOS I'],
        6: ['COM002', 'SISTEMAS DE COMPUTAÇÃO'], 7: ['MAT003', 'CÁLCULO DIFERENCIAL E INTEGRAL I'],
        8: ['MAT002', 'GEOMETRIA ANALÍTICA E ÁLGEBRA LINEAR'], 9: ['COM004', 'ALGORITMOS E ESTRUTURA DE DADOS II'],
        10: ['COM005', 'ORGANIZAÇÃO E ARQUITETURA DE COMPUTADORES'], 11: ['COM006', 'TEORIA DA COMPUTAÇÃO'],
        12: ['COM007', 'ADMINISTRAÇÃO I'], 13: ['COM008', 'FUNDAMENTOS DE ECONOMIA'],
        14: ['COM009', 'ALGORITMOS E ESTRUTURA DE DADOS III'], 15: ['COM010', 'SISTEMAS OPERACIONAIS'],
        16: ['COM011', 'ADMINISTRAÇÃO II'], 17: ['COM012', 'FUNDAMENTOS DE CONTABILIDADE'],
        18: ['COM013', 'DIREITO LEGISLAÇÃO EM INFORMÁTICA'], 19: ['COM014', 'LINGUAGENS DE PROGRAMAÇÃO'],
        20: ['COM015', 'BANCO DE DADOS I'], 21: ['COM016', 'PROGRAMAÇÃO ORIENTADA A OBJETOS'],
        22: ['COM017', 'PESQUISA OPERACIONAL'], 23: ['COM018', 'GESTÃO DE SISTEMAS DE INFORMAÇÃO'],
        24: ['COM019', 'SISTEMAS DE APOIO À DECISÃO'], 25: ['COM020', 'ENGENHARIA WEB'],
        26: ['COM021', 'BANCO DE DADOS II'], 27: ['COM022', 'REDES DE COMPUTADORES I'],
        28: ['COM023', 'ENGENHARIA DE SOFTWARE I'], 29: ['COM024', 'INTELIGÊNCIA ARTIFICIAL'],
        30: ['COM025', 'INFORMÁTICA E SOCIEDADE'], 31: ['COM026', 'REDES DE COMPUTADORES II'],
        32: ['COM027', 'ENGENHARIA DE SOFTWARE II'], 33: ['COM028', 'INTERFACE HOMEM MÁQUINA'],
        34: ['COM029', 'TRABALHO COOPERATIVO APOIADO POR COMPUTADOR'], 35: ['COM030', 'COMPORTAMENTO ORGANIZACIONAL'],
        36: ['COM032', 'SISTEMAS DISTRIBUÍDOS'], 37: ['COM033', 'GERÊNCIA DE PROJETOS DE SOFTWARE'],
        38: ['COM034', 'SEGURANÇA E AUDITORIA DE SISTEMAS DE INFORMAÇÃO'], 39: ['COM035', 'EMPREENDEDORISMO'],
        40: ['COM036', 'PROJETO ORIENTADO I (TCC)'], 41: ['COM038', 'PROJETO ORIENTADO II (TCC)'],
        42: ['COM003', 'TEORIA GERAL DOS SISTEMAS'],
        43: ['MAT004', 'ESTATÍSTICA'], 44: ['COM059', 'LEITURA E PRODUÇÃO DE TEXTOS'],
        45: ['COM060', 'METODOLOGIA DO TRABALHO E DA PESQUISA CIENTÍFICA E TECNOLÓGICA']
    };

####################################################### PARÂMETROS #####################################################

    # ocupacao = [578, 511, 393, 516, 502, 782, 402, 478, 593, 387, 355, 513, 368, 370, 321, 285, 252, 421, 405, 303, 248, 292, 232, 247, 320,
    #                    264, 181, 174, 253, 281, 319, 176, 196, 200, 291, 269, 152, 165, 161, 286, 272, 318, 742, 221, 342, 214];

    # retidos = [359, 196, 80, 263, 78, 431, 148, 184, 371, 156, 113, 270, 96, 70, 99, 21, 27, 118, 60, 70, 64, 63, 56, 27, 17, 31,
    #            44, 12, 28, 92, 33, 8, 4, 16, 12, 39, 4, 1, 4, 16, 102, 202, 514, 81, 86, 46];

    # creditos de cada disciplina
    creditos = [4, 4, 4, 4, 3, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 2, 4, 4, 3, 3,
                3, 4, 4, 4, 3, 4, 8, 4, 4, 4, 3];

    #índices de retenção (porcentagens) nas respectivas disciplinas
    indicesRetencao = [62, 38, 20, 51, 15, 55, 37, 69, 63, 40, 32, 53, 26, 19, 31, 7, 11, 28, 15, 23, 26, 22, 24, 11, 5,
                       12, 24, 7, 11, 33, 10, 5, 2, 8, 4, 14, 3, 1, 2, 6, 37, 63, 38, 37, 25, 21];

    # disciplinas e seus respectivos pre-requisitos
    prerequisitos = {5: [1], 9: [5], 10: [6], 14: [9], 16: [12], 43: [7], 15: [9, 10], 20: [9], 19: [9], 22: [5, 8],
                     21: [9], 26: [20], 28: [21], 25: [21], 29: [9], 27: [15], 32: [28], 33: [28], 31: [27],
                     37: [32], 40: [32], 38: [31], 36: [31], 41: [40]
                     };

    #disciplinas que devem estar sempre no primeiro período
    disciplinasNivelamento = [0, 1, 2, 4, 44]

    # disciplinas que devem sempre estar no penúltimo período
    disciplinasPenultimoPeriodo = [40]

    # disciplinas que devem sempre estar no último período
    disciplinasUltimoPeriodo = [41]

     # parametros
    quantidadeDisciplinas = len(codigosDisciplinasTraducao);
    quantidadePeriodos = 9;
    #considerando que a quantidade mínima de disciplinas é 2 e não existir disciplinas com menos de 2 créditos
    cargaMinimaPorPeriodo = 4;
    #regulamento da graduação diz que a carga máxima são 36 créditos
    cargaMaximaPorPeriodo = 36;
    quantidadeMinimaDisciplinasPorPeriodo = 2;
    quantidadeMaximaDisciplinasPorPeriodo = 10;

    #números que indicam os 'graus' crescentes de relações entre as disciplinas
    relacaoNivel1 = 1;
    relacaoNivel2 = 2;
    relacaoNivel3 = 3;
    relacaoNivel4 = 4;
    relacaoNivel5 = 5;
    relacaoNivel6 = 6;
    relacaoNivel7 = 7;
    relacaoNivel8 = 8;
    relacaoNivel9 = 9;#apenas para pré-requisitos

    #Lower e upper bounds referentes aos critérios
    minCarga = 20
    maxCarga = 36
    minRetencao = 160
    maxRetencao = 271
    minRelacao = 403
    maxRelacao = 3717

    #parâmetros que controlam as distâncias entre disciplinas de acordo com o grau de relação entre estas
    diferencaMinimaPeriodosRelacaoNivel3 = 0;
    diferencaMaximaPeriodosRelacaoNivel9 = 2;
    #diferencaMaximaPeriodosRelacaoMaiorNivel4 = 8;

    # codigos das disciplinas
    disciplinas = range(quantidadeDisciplinas);
    # codigos dos períodos
    periodos = range(quantidadePeriodos);

    #distância entre os semestres (referência do artigo (Uysal, 2014))
                          #0 #1 #2 #3  #4  #5  #6  #7  #8
    distanciaSemestres = [[0, 1, 4, 9, 16, 25, 36, 49, 64],#0
                          [100, 0, 1, 4, 9, 16, 25, 36, 49],#1
                          [100, 100, 0, 2, 9, 16, 25, 36, 49],#2
                          [100, 100, 100, 0, 1, 4, 9, 16, 25],#3
                          [100, 100, 100, 100, 0, 2, 9, 16, 25],#4
                          [100, 100, 100, 100, 100, 0, 1, 4, 9],#5
                          [100, 100, 100, 100, 100, 100, 0, 2, 9],#6
                          [100, 100, 100, 100, 100, 100, 100, 0, 1],#7
                          [100, 100, 100, 100, 100, 100, 100, 100, 0]]#8

    #matriz de relação entre as disciplinas
                                   #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45
    relacaoRelacaoDisciplinas = [  [0, 0, 0, 0, 0, 0, 0, 8, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #0
                                   [0, 0, 0, 0, 0, 9, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #1
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #2
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #3
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #4
                                   [0, 0, 0, 3, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #5
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #6
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0], #7
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #8
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #9
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #10
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #11
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 9, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #12
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #13
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #14
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #15
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0], #16
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #17
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #18
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #19
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #20
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0], #21
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #22
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #23
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #24
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 5, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0], #25
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #26
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0], #27
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #28
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #29
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #30
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 9, 0, 0, 0, 0, 0, 0, 0], #31
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 9, 0, 0, 0, 0, 0], #32
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0], #33
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0], #34
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #35
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #36
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #37
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #38
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #39
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0], #40
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #41
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #42
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #43
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7], #44
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #45
                                   ]


    #################################################### VARIÁVEIS #####################################################

    # X é uma lista que, para cada disciplina, tem-se uma outra lista com valores que indicam se a disciplina está em um determinado período, resultando em uma matriz
    X = []
    for i in disciplinas:
        X.append([])
        for j in periodos:
            X[i].append(modelo.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="x" + str(i) + str(j)))

################################################## FUNÇÃO OBJETIVO #####################################################

    #pesos para os termos da função objetivo
    #TODO: eliminar hardcoded
    a = [0,1,2,3,4,5,6,7,8,9,10]
    pesos = []
    combinacoes = 0
    runtime = 0
    for i in a:
        for j in a:
            for k in a:
                if(i+j+k == 10):
                    pesos.append([])
                    pesos[combinacoes].append(i/10)
                    pesos[combinacoes].append(j/10)
                    pesos[combinacoes].append(k/10)
                    combinacoes += 1

    for c in range(combinacoes):
        pesoCarga = pesos[c][0]
        pesoRetencao = pesos[c][1]
        pesoRelacao = pesos[c][2]

        #C, IR e RD são variáveis que compõem a função objetivo
        C = modelo.addVar(lb=cargaMinimaPorPeriodo, vtype=GRB.INTEGER, obj=1, name="maxCarga")
        IR = modelo.addVar(lb=0, vtype=GRB.INTEGER, obj=1, name="indiceRetencao")
        # RD é o somátório do grau de relação entre pares de disciplinas, multiplicado pela distância entre estas
        RD = quicksum(relacaoRelacaoDisciplinas[ii][i]*distanciaSemestres[jj][j]*X[i][j]*X[ii][jj] for ii in disciplinas for i in disciplinas for jj in periodos for j in periodos)
        #RD = modelo.addVar(lb=0, vtype=GRB.INTEGER, obj=1, name="relacaoDistancia")

        #modelo.setObjective(quicksum(X[i][j] * indicesRetencao[i] for i in disciplinas for j in periodos), GRB.MAXIMIZE)
        #modelo.setObjective(pesoCarga*C + pesoRetencao*IR + pesoRelacao*RD, GRB.MAXIMIZE)
        modelo.setObjective(pesoCarga * (C-minCarga)/(maxCarga-minCarga) +
                            pesoRetencao*(IR-minRetencao)/(maxRetencao-minRetencao) +
                            pesoRelacao*(RD-minRelacao)/(maxRelacao-minRelacao), GRB.MINIMIZE)
    ################################################## RESTRIÇÕES ##########################################################

        # Disciplinas de nivelamento obrigatoriamente no primeiro período
        # for i in disciplinasNivelamento:
        #     modelo.addConstr(X[i][0], GRB.EQUAL, 1,
        #                      name="DisciplinaNivelamento" + str(i))

        # Flexibilização para que disciplinas de nivelamento possam estar até o 2º período
        for i in disciplinasNivelamento:
            modelo.addConstr(
                            (quicksum(X[i][j] * j for j in periodos)),
                            GRB.LESS_EQUAL, 1, name="DisciplinaNivelamento" + str(i));

        # TCCI deve estar no penúltimo período
        for i in disciplinasPenultimoPeriodo:
            modelo.addConstr(X[i][7], GRB.EQUAL, 1,
                             name="DisciplinaPenultimoPeriodo" + str(i))

        # TCCII deve estar no último período
        for i in disciplinasUltimoPeriodo:
            modelo.addConstr(X[i][8], GRB.EQUAL, 1,
                             name="DisciplinaUltimoPeriodo" + str(i))

        # Complementa restrição de pre-requisitos, adicionando restrição que impede que uma disciplina que possua pre-requisito
        # localize-se no primeiro período
        for i in prerequisitos:
            modelo.addConstr(X[i][0], GRB.EQUAL, 0,
                             name="PrerequisitoPeriodo1ZERO" + str(i))

        # Adiciona restrições quanto aos pré-requisitos(pre-requisito de uma disciplina deve estar em um período anterior ao
        # desta)
        for i in disciplinas:
            if i in prerequisitos:
                for pr in prerequisitos[i]:
                    for j in range(1, quantidadePeriodos):
                        # for j in range(0, quantidadePeriodos):# garantiria que a regra de pre-requisitos, mas é necessário
                        # uma regra explícita
                        modelo.addConstr((quicksum(X[pr][ppr] for ppr in range(j)) - X[i][j]), GRB.GREATER_EQUAL, 0,
                                         name="PrerequisitoSumDe" + str(i) + "=" + str(pr) + str(j))

        # Adiciona restrição de quantidade de períodos em que uma disciplina poderá estar(em apenas um período)
        for i in disciplinas:
            modelo.addConstr(quicksum(X[i][j] for j in periodos), GRB.EQUAL, 1,
                             name="QuantidadeDisciplinasPeriodo[%d]" % i)

        for j in periodos:
            # Adiciona restrição de carga mínima de um período
            modelo.addConstr(quicksum(X[i][j] * creditos[i] for i in disciplinas), GRB.GREATER_EQUAL, cargaMinimaPorPeriodo,
                             name="CargaMinima[%d]" % j)

            # Adiciona restrição de carga máxima de um período (a carga máxima de um período deve ser sempre menor ou igual
            # ao valor máximo atual na definição dos valores de C)
            modelo.addConstr(quicksum(X[i][j] * creditos[i] for i in disciplinas), GRB.LESS_EQUAL, C,
                             name="CargaMaxima[%d]" % j)

            # Adiciona restrição de quantidade mínima de disciplinas em um período
            modelo.addConstr(quicksum(X[i][j] for i in disciplinas), GRB.GREATER_EQUAL,
                             quantidadeMinimaDisciplinasPorPeriodo,
                             name="QuantidadeDisciplinasMinima[%d]" % j)

            # Adiciona restrição de quantidade máxima de disciplinas em um período
            modelo.addConstr(quicksum(X[i][j] for i in disciplinas), GRB.LESS_EQUAL, quantidadeMaximaDisciplinasPorPeriodo,
                             name="QuantidadeDisciplinasMaxima[%d]" % j)

            # Adiciona restrição de soma de índice de retenção máximo a um período (o índice de retenção de um período deve
            # ser sempre menor ou igual ao valor máximo atual na definição dos valores de IR)
            modelo.addConstr(quicksum(X[i][j] * indicesRetencao[i] for i in disciplinas), GRB.LESS_EQUAL, IR,
                             name="IndiceRetencao[%d]" % j)

        #Adiciona restrições quanto ao posicionamento das disciplinas baseado nas relações
        for i in disciplinas:
            for ii in disciplinas:
                if (relacaoRelacaoDisciplinas[i][ii] >= relacaoNivel3):
                    #Adiciona restrição de posicionamento anterior de disciplina (com grau de relação igual a nível 3) à outra.
                    #Se o grau de relação for maior ou igual a 3, j tem que estar no mesmo período ou posterior a i
                    modelo.addConstr(
                        (quicksum(X[ii][jj] * jj for jj in periodos)) - (quicksum(X[i][j] * j for j in periodos)),
                        GRB.GREATER_EQUAL, diferencaMinimaPeriodosRelacaoNivel3);

                # Adiciona restrição de distância entre disciplinas que possui grau 9 de relação (apenas pré-requisitos)
                if (relacaoRelacaoDisciplinas[i][ii] == relacaoNivel9):
                    modelo.addConstr(
                        (quicksum(X[ii][jj] * jj for jj in periodos)) - (quicksum(X[i][j] * j for j in periodos)),
                        GRB.LESS_EQUAL, diferencaMaximaPeriodosRelacaoNivel9);

        #Referência para tratar variável nao linear https://support.gurobi.com/hc/en-us/community/posts/360061829412-Why-Objective-must-be-liearn-for-multi-objective-model-in-Gurobi-
        #Neste caso, a variável seria quadrática
        #modelo.addConstr(quicksum(relacaoRelacaoDisciplinas[ii][i]*distanciaSemestres[jj][j]*X[i][j]*X[ii][jj] for ii in disciplinas for i in disciplinas for jj in periodos for j in periodos) == RD);

    ############################################### EXECUÇÃO DA FUNÇÃO OBJETIVO ############################################

        #Realiza o balanceamento
        modelo.optimize()
        runtime = runtime + modelo.Runtime
        print ('runtime is', runtime)

    ############################################## IMPRESSÃO DOS RESULTADOS ################################################

       # Escreve o modelo/resultado em um arquivo de texto
        modelo.write('curriculumbalancing.lp')


        # impressão dos resultados
        print("\n")
        print("Solução: "+ str(c))
        print("\n")
        resultados.append("Solução: "+ str(c))
        resultados.append("\n")
        resultados.append("\n")
        imprimirPesos(resultados, pesoCarga, pesoRetencao, pesoRelacao)
        print("\n")
        imprimirValoresVariaveis(resultados, C, IR, RD)
        print("\n")
        imprimirSomatorioCargasPorPeriodo(periodos, creditos, disciplinas, resultados)
        print("\n")
        imprimirSomatorioIndicesRetencao(periodos, indicesRetencao, disciplinas, resultados)
        print("\n")
        imprimirGrade(periodos, disciplinas, codigosDisciplinasTraducao, creditos, indicesRetencao, resultados)
        imprimirValoresParaFronteiraPareto(resultadosPareto, pesoCarga, pesoRetencao, pesoRelacao)

        print('Valor função objetivo: %g' % modelo.objVal)
        resultados.append('Valor função objetivo: %g' % modelo.objVal)

        data_e_hora_atuais = datetime.now()
        data_e_hora_em_texto = str(datetime.now())
        data_e_hora_em_texto = data_e_hora_em_texto.replace(":", "_")
        data_e_hora_em_texto = data_e_hora_em_texto.replace(" ", "_")
        arquivo = open("resultadosSINUFVJM/iteracao "+data_e_hora_em_texto+".txt", "a", encoding='utf-8')
        arquivo.writelines(resultados)
        resultados.clear()
        arquivo.close()

    data_e_hora_atuais_pareto = datetime.now()
    data_e_hora_em_texto_pareto = str(datetime.now())
    data_e_hora_em_texto_pareto = data_e_hora_em_texto_pareto.replace(":", "_")
    data_e_hora_em_texto_pareto = data_e_hora_em_texto_pareto.replace(" ", "_")
    arquivo_pareto = open("resultadosSINUFVJM/dadosPareto "+data_e_hora_em_texto_pareto+".txt", "a", encoding='utf-8')
    arquivo_pareto.writelines(resultadosPareto)
    arquivo_pareto.close()

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')
