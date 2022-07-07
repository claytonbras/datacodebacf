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

    #Método que imprimir a matriz disciplina x periodo
    # def imprimirMatriz(disciplinas, periodos):
    #
    #     print("MATRIZ DISCIPLINA X PERÍODO")
    #
    #     for i in disciplinas:
    #         print("D " + str(i) + '|', end=' ')
    #         for j in periodos:
    #             print(int(round(X[i][j].x)), end=' ')
    #         print("\n")

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
        0: ['DCC111', 'MATEMATICA DISCRETA'], 1: ['DCC050', 'INTRODUCAO A CIENCIA DA COMPUTACAO'],
        2: ['DCC003', 'ALGORITMOS E ESTRUTURA DE DADOS I'], 3: ['MAT001', 'CALCULO DIFERENCIAL E INTEGRAL I'],
        4: ['MAT038', 'GEOMETRIA ANALITICA E ALGEBRA LINEAR'], 5: ['FIS054', 'INTRODUCAO A FISICA EXPERIMENTAL'],

        6: ['DCC004', 'ALGORITMOS E ESTRUTURA DE DADOS II'], 7: ['MAT039', 'CALCULO DIFERENCIAL E INTEGRAL II'],
        8: ['FIS065', 'FUNDAMENTOS DE MECANICA'], 9: ['MAT034', 'ALGEBRA A'], 10: ['DCC114', 'INTRODUCAO AOS SISTEMAS LOGICOS'],

        11: ['DCC033', 'ANALISE NUMERICA'],
        12: ['DCC005', 'ALGORITMOS E ESTRUTURA DE DADOS III'], 13: ['DCC006', 'ORGANIZACAO DE COMPUTADORES I'],
        14: ['MAT002', 'CALCULO DIFERENCIAL E INTEGRAL III'], 15: ['ECN140', 'INTRODUCAO A ECONOMIA'],
        16: ['EST032', 'PROBABILIDADE'],

        17: ['MAT040', 'EQUACOES DIFERENCIAIS C'], 18: ['DCC008', 'SOFTWARE BASICO'],
        19: ['DCC129', 'FUNDAMENTOS DA TEORIA DA COMPUTACAO'], 20: ['DCC007', 'ORGANIZACAO DE COMPUTADORES II'],
        21: ['FIS069', 'FUNDAMENTOS DE ELETROMAGNETISMO'], 22: ['CAD011', 'ADMINISTRACAO'],

        23: ['DCC035', 'PESQUISA OPERACIONAL'],
        24: ['DCC605', 'SISTEMAS OPERACIONAIS'], 25: ['DCC024', 'LINGUAGENS DE PROGRAMACAO'],
        26: ['DCC052', 'PROGRAMACAO MODULAR'], 27: ['CIC001', 'CALCULO FINANCEIRO E CUSTOS'],

        28: ['DCC011', 'INTRODUCAO A BANCO DE DADOS'],
        29: ['DCC023', 'REDES DE COMPUTADORES'], 30: ['DCC053', 'COMPILADORES I'],
        31: ['LET200', 'OFICINA DE LINGUA PORTUGUESA: LEITURA E PRODUCAO DE TEXTOS'],

        32: ['DCC603', 'ENGENHARIA DE SOFTWARE'],
        33: ['DCC604', 'PROJETO ORIENTADO EM COMPUTACAO I'],

        34: ['DCC606', 'COMPUTADORES E SOCIEDADE'],
        35: ['DCC009', 'PROJETO ORIENTADO EM COMPUTACAO II']
    };

####################################################### PARÂMETROS #####################################################

    # creditos de cada disciplina
    creditos = [4, 2, 4, 6, 4, 3,    4, 4, 4, 4, 4,    4, 4, 4, 4, 4, 4,    4, 4, 4, 4, 4, 4,    4, 4, 4, 4, 4,    4, 4, 4, 4,    4, 6,   4, 6];

    #índices de retenção (porcentagens) nas respectivas disciplinas
    indicesRetencao = [27, 9, 17, 39, 34, 13,   36, 35, 35, 23, 19,  19, 31, 23, 37, 13, 36,  31, 19, 9, 18, 43, 5,  35, 11, 14, 7, 7,  6, 19, 15, 7,  5, 7,  2, 8];

    # disciplinas e seus respectivos pre-requisitos
    prerequisitos = {7: [3, 4], 8: [3], 6: [2], 14: [7], 17: [7], 12: [6], 13: [10], 21: [8], 20: [13], 30: [19], 35: [33]
                     };

    #disciplinas que devem estar sempre no primeiro período
    disciplinasNivelamento = [0, 1, 2, 3, 4, 5]

    # disciplinas que devem sempre estar no penúltimo período
    disciplinasPenultimoPeriodo = [33]

    # disciplinas que devem sempre estar no último período
    disciplinasUltimoPeriodo = [35]

    # parametros
    quantidadeDisciplinas = len(codigosDisciplinasTraducao);
    quantidadePeriodos = 8;
    quantidadeMinimaDisciplinasPorPeriodo = 2;
    quantidadeMaximaDisciplinasPorPeriodo = 10;
    #Valores retirados do documento de normas da graduação e análise da grade
    cargaMinimaPorPeriodo = 12#extraído da visualização da grade atual
    cargaMaximaPorPeriodo = 24#extraído da visualização da grade atual

    #Lower e upper bounds referentes aos critérios
    minCarga = 20
    maxCarga = 24
    minRetencao = 90
    maxRetencao = 714
    minRelacao = 142
    maxRelacao = 2465

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

    #parâmetros que controlam as distâncias entre disciplinas de acordo com o grau de relação entre estas
    diferencaMinimaPeriodosRelacaoNivel3 = 0;
    diferencaMaximaPeriodosRelacaoNivel9 = 2;
    #diferencaMaximaPeriodosRelacaoMaiorNivel4 = 8;

    # codigos das disciplinas
    disciplinas = range(quantidadeDisciplinas);
    # codigos dos períodos
    periodos = range(quantidadePeriodos);

    #distância entre os semestres (referência do artigo (Uysal, 2014))
                          #0 #1 #2 #3  #4  #5  #6  #7
    distanciaSemestres = [[0, 1, 4, 9, 16, 25, 36, 49],#0
                          [100, 0, 1, 4, 9, 16, 25, 36],#1
                          [100, 100, 0, 2, 9, 16, 25, 36],#2
                          [100, 100, 100, 0, 1, 4, 9, 16],#3
                          [100, 100, 100, 100, 0, 2, 9, 16],#4
                          [100, 100, 100, 100, 100, 0, 1, 4],#5
                          [100, 100, 100, 100, 100, 100, 0, 2],#6
                          [100, 100, 100, 100, 100, 100, 100, 0]]#7

#matriz de relação entre as disciplinas
                                 #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35
    relacaoRelacaoDisciplinas = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #0
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #1
                                 [8, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #2
                                 [0, 0, 0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #3
                                 [0, 0, 0, 0, 0, 0, 0, 9, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #4
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #5
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0], #6
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #7
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #8
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #9
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #10
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #11
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #12
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #13
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #14
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0], #15
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #16
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #17
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #18
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0], #19
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #20
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #21
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #22
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #23
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0], #24
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #25
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #26
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #27
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #28
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #29
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #30
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #31
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #32
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9], #33
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #34
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  #35
                                 ]

    #################################################### VARIÁVEIS #####################################################

    # X é uma lista que, para cada disciplina, tem-se uma outra lista com valores que indicam se a disciplina está em um determinado período
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
        C = modelo.addVar(lb=cargaMinimaPorPeriodo, ub=cargaMaximaPorPeriodo, vtype=GRB.INTEGER, obj=1, name="maxCarga")
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
            modelo.addConstr(X[i][6], GRB.EQUAL, 1,
                             name="DisciplinaPenultimoPeriodo" + str(i))

        # TCCII deve estar no último período
        for i in disciplinasUltimoPeriodo:
            modelo.addConstr(X[i][7], GRB.EQUAL, 1,
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
                    #Adiciona restrição de posicionamento anterior de disciplina (com grau de relação igual a nível 3) à outra
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
        print('runtime is', runtime)

    ############################################## IMPRESSÃO DOS RESULTADOS ################################################

       # Escreve o modelo/resultado em um arquivo de texto
        modelo.write('curriculumbalancing.lp')

        #impressão dos resultados
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
        arquivo = open("resultadosCCUFMG/iteracao "+data_e_hora_em_texto+".txt", "a", encoding='utf-8')
        arquivo.writelines(resultados)
        resultados.clear()
        arquivo.close()

    data_e_hora_atuais_pareto = datetime.now()
    data_e_hora_em_texto_pareto = str(datetime.now())
    data_e_hora_em_texto_pareto = data_e_hora_em_texto_pareto.replace(":", "_")
    data_e_hora_em_texto_pareto = data_e_hora_em_texto_pareto.replace(" ", "_")
    arquivo_pareto = open("resultadosCCUFMG/dadosPareto "+data_e_hora_em_texto_pareto+".txt", "a", encoding='utf-8')
    arquivo_pareto.writelines(resultadosPareto)
    arquivo_pareto.close()

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')
