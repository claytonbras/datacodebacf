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
# import time
# start_time = time.time()
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
        0: ['UNI035', 'INTRODUCAO A ENGENHARIA DE SISTEMAS'], 1: ['ELE064', 'ANALISE DE CIRCUITOS ELETRICOS I'],
        2: ['DCC003', 'ALGORITMOS E ESTRUTURA DE DADOS I'], 3: ['MAT001', 'CALCULO DIFERENCIAL E INTEGRAL I'],
        4: ['MAT038', 'GEOMETRIA ANALITICA E ALGEBRA LINEAR'],

        5: ['DCC033', 'ANALISE NUMERICA'],
        6: ['DCC004', 'ALGORITMOS E ESTRUTURA DE DADOS II'], 7: ['MAT039', 'CALCULO DIFERENCIAL E INTEGRAL II'],
        8: ['FIS065', 'FUNDAMENTOS DE MECANICA'], 9: ['ELT059', 'SISTEMAS DIGITAIS'],


        10: ['ELE065', 'ANALISE DE CIRCUITOS ELETRICOS II'], 11: ['MAT015', 'EQUACOES DIFERENCIAIS A'],
        12: ['FIS067', 'FUNDAMENTOS DE MECANICA DOS SOLIDOS E FLUIDOS'], 13: ['MAT002', 'CALCULO DIFERENCIAS E INTEGRAL III'],
        14: ['ELT029', 'LABORATORIO DE SISTEMAS DIGITAIS'],
        15: ['ELE077', 'OTIMIZACAO NAO LINEAR'], 16: ['ELE078', 'PROGRAMACAO ORIENTADA A OBJETOS'],


        17: ['DCC005', 'ALGORITMOS E ESTRUTURAS DE DADOS III'], 18: ['ELT060', 'ANALISE DE SISTEMAS DINAMICOS LINEARES'],
        19: ['MAT016', 'EQUACOES DIFERENCIAIS B'], 20: ['FIS069', 'FUNDAMENTOS DE ELETROMAGNETISMO'],
        21: ['FIS066', 'FUNDAMENTOS DE TERMODINAMICA'],  22: ['ELT075', 'REDES NEURAIS ARTIFICIAIS'],

        23: ['ELT079', 'DISPOSITIVOS E CIRCUITOS ELETRONICOS BASICOS'], 24: ['ELE079', 'ELETROMAGNETISMO COMPUTACIONAL'],
        25: ['EMA255', 'FLUIDOS E TERMODINAMICA COMPUTACIONAL'], 26: ['ELE156', 'LABORATORIO DE CIRCUITOS E ELETRONICA C'],
        27: ['ELE092', 'LABORATORIO DE PROJETO I'], 28: ['EST032', 'PROBABILIDADE'],


        29: ['ELT009', 'ENGENHARIA DE CONTROLE'], 30: ['ELE080', 'ENGENHARIA DE SOFTWARE'],
        31: ['FIS070', 'FUNDAMENTOS DE OPTICA'], 32: ['ELT080', 'LABORATORIO DE CIRCUITOS ELETRONICOS E PROJETOS'],
        33: ['ELE081', 'LABORATORIO DE PROJETO II'], 34: ['ELE082', 'PESQUISA OPERACIONAL'],


        35: ['ELE083', 'COMPUTACAO EVOLUCIONARIA'], 36: ['ELE084', 'LABORATORIO DE PROJETO III'],
        37: ['ELE093', 'MODELOS ESTATISTICOS E INFERENCIA'], 38: ['ELE042', 'PROCESSAMENTO DE SINAIS'],
        39: ['ELT005', 'SISTEMAS PROCESSADORES E PERIFERICOS'], 40: ['ELT016', 'TECNICAS DE MODELAGEM DE SISTEMAS DINAMICOS'],

        41: ['EEE017', 'CONFIABILIDADE DE SISTEMAS'], 42: ['ELE085', 'CONVERSORES ELETROMECANICOS'],
        43: ['ELE086', 'LABORATORIO DE PROJETO IV'], 44: ['ELE087', 'PROJETO MULTIDISCIPLINAR'],
        45: ['DCC023', 'REDES DE COMPUTADORES'], 46: ['ELE075', 'SISTEMAS NEBULOSOS'],
        47: ['ELE088', 'TEORIA DA DECISAO'],

        48: ['ELE094', 'LABORATORIO DE PROJETO V'],

	    49: ['EEE018', 'TRABALHO DE CONCLUSAO DE CURSO I'],

        50: ['EEE019', 'TRABALHO DE CONCLUSAO DE CURSO II']

    };

####################################################### PARÂMETROS #####################################################

    # creditos de cada disciplina
    creditos = [1, 2, 4, 6, 4,    4, 4, 4, 4, 3,    2, 4, 1, 4, 2, 2, 4,    4, 4, 4, 4, 2, 2,    4, 4, 4, 4, 2, 2,     4, 4, 2, 2, 4, 4,     2, 4, 3, 4, 5, 2,
                4, 2, 4, 4, 4, 2, 2,   4,   6,   6];

    #índices de retenção (porcentagens) nas respectivas disciplinas
    indicesRetencao = [7, 48, 38, 39, 37,    33, 40, 35, 43, 33,    46, 44, 25, 39, 11, 34, 28,   39, 48, 36, 38, 39, 26,    31, 18, 16, 7, 3, 26,
                       38, 3, 29, 2, 3, 13,    6, 2, 5, 31, 10, 16,    6, 8, 0, 0, 24, 12, 7,   0,   5,   13];

    # disciplinas e seus respectivos pre-requisitos
    prerequisitos = {5: [2], 6: [2], 7: [3, 4], 8: [3],  10: [1], 11: [7], 12: [8], 13: [7], 14: [9], 15: [5], 16: [6], 17: [6], 18: [11], 19: [7], 20: [7],
                     22: [11], 23: [10], 24: [20], 25: [21], 26: [10], 27: [14], 28: [3], 30: [15], 32: [23], 33: [27], 36: [33], 37: [28], 39: [14], 40: [14],
                     41: [28], 43: [36], 44: [43], 48: [43], 50: [49]};

    #disciplinas que devem estar sempre no primeiro período
    disciplinasNivelamento = [0, 1, 2, 3, 4]

    # disciplinas que devem sempre estar no penúltimo período
    disciplinasPenultimoPeriodo = [49]

    # disciplinas que devem sempre estar no último período
    disciplinasUltimoPeriodo = [50]

    quantidadeDisciplinas = len(codigosDisciplinasTraducao);
    quantidadePeriodos = 11;
    quantidadeMinimaDisciplinasPorPeriodo = 1;
    quantidadeMaximaDisciplinasPorPeriodo = 8;

    #Valores retirados do documento de normas da graduação e análise da grade
    cargaMinimaPorPeriodo = 10#extraído da visualização da grade atual(último período com duas disciplinas e carga 10)
    cargaMaximaPorPeriodo = 23#extraído da visualização da grade atual(primeiro período com 5 disciplinas e carga 20)

    #Lower e upper bounds referentes aos critérios
    minCarga = 16
    maxCarga = 23
    minRetencao = 133
    maxRetencao = 250
    minRelacao = 439
    maxRelacao = 3708

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
                          #0 #1 #2 #3  #4  #5  #6  #7  #8  #9  #10  #11  #12
    distanciaSemestres = [[0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100],#0
                          [100, 0, 1, 4, 9, 16, 25, 36, 49, 64, 81],#1
                          [100, 100, 0, 2, 9, 16, 25, 36, 49, 64, 81],#2
                          [100, 100, 100, 0, 1, 4, 9, 16, 25, 36, 49],#3
                          [100, 100, 100, 100, 0, 2, 9, 16, 25, 36, 49],#4
                          [100, 100, 100, 100, 100, 0, 1, 4, 9, 16, 25],#5
                          [100, 100, 100, 100, 100, 100, 0, 2, 9, 16, 25],#6
                          [100, 100, 100, 100, 100, 100, 100, 0, 1, 9, 16],#7
                          [100, 100, 100, 100, 100, 100, 100, 100, 0, 2, 9],#8
                          [100, 100, 100, 100, 100, 100, 100, 100, 100, 0, 1],#9
                          [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 0]]#10
                          #[100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 0]]#11

    #matriz de relação entre as disciplinas
    relacaoRelacaoDisciplinas = [   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #0
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #1
                                    [0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #2
                                    [0, 0, 0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #3
                                    [0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #4
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #5
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #6
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 9, 0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #7
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #8
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #9
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #10
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #11
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #12
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #13
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #14
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #15
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #16
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #17
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #18
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #19
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #20
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #21
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #22
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #23
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #24
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #25
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #26
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #27
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0], #28
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #29
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #30
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #31
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #32
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #33
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #34
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #35
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0], #36
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #37
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #38
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0], #39
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #40
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #41
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #42
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 9, 0, 0], #43
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #44
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #45
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #46
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #47
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #48
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9], #49
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] #50


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

        # modelo.setObjective(pesoRelacao*RD, GRB.MAXIMIZE)
        #modelo.setObjective(pesoCarga*C + pesoRetencao*IR + pesoRelacao*RD, GRB.MINIMIZE)
        # modelo.setObjective(quicksum(X[i][j] * indicesRetencao[i] for i in disciplinas for j in periodos), GRB.MAXIMIZE)

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
            modelo.addConstr(X[i][9], GRB.EQUAL, 1,
                             name="DisciplinaPenultimoPeriodo" + str(i))

        # TCCII deve estar no último período
        for i in disciplinasUltimoPeriodo:
            modelo.addConstr(X[i][10], GRB.EQUAL, 1,
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
        arquivo = open("resultadosESIUFMG/iteracao "+data_e_hora_em_texto+".txt", "a", encoding='utf-8')
        arquivo.writelines(resultados)
        resultados.clear()
        arquivo.close()

    data_e_hora_atuais_pareto = datetime.now()
    data_e_hora_em_texto_pareto = str(datetime.now())
    data_e_hora_em_texto_pareto = data_e_hora_em_texto_pareto.replace(":", "_")
    data_e_hora_em_texto_pareto = data_e_hora_em_texto_pareto.replace(" ", "_")
    arquivo_pareto = open("resultadosESIUFMG/dadosPareto "+data_e_hora_em_texto_pareto+".txt", "a", encoding='utf-8')
    arquivo_pareto.writelines(resultadosPareto)
    arquivo_pareto.close()

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')
