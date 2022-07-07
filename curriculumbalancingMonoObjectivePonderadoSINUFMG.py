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
        0: ['CAD103-DIG', 'ADMINISTRACAO T.G.A.'], 1: ['DCC044-DIG', 'FUNDAMENTOS DE SISTEMAS DE INFORMACAO'],
        2: ['DCC003-DIG', 'ALGORITMOS E ESTRUTURA DE DADOS I'], 3: ['MAT001-DIG', 'CALCULO DIFERENCIAL E INTEGRAL I'],
        4: ['MAT038-DIG', 'GEOMETRIA ANALITICA E ALGEBRA LINEAR'],

        5: ['DCC111-DIG', 'MATEMATICA DISCRETA'],
        6: ['DCC004-DIG', 'ALGORITMOS E ESTRUTURA DE DADOS II'], 7: ['MAT039-DIG', 'CALCULO DIFERENCIAL E INTEGRAL II'],
        8: ['ECN101-DIG', 'ECONOMIA A I'],

        9: ['MAT034-DIG', 'ALGEBRA A'],
        10: ['TGI004-DIG', 'USUARIOS DA INFORMACAO'], 11: ['DCC114-DIG', 'INTRODUCAO AOS SISTEMAS LOGICOS'],
        12: ['DCC005-DIG', 'ALGORITMOS E ESTRUTURA DE DADOS III'], 13: ['EST031-DIG', 'ESTATISTICA E PROBABILIDADES'],

        14: ['DCC011-DIG', 'INTRODUCAO A BANCO DE DADOS'], 15: ['CAD163-DIG', 'ADMINISTRACAO DE RECURSOS HUMANOS'],
        16: ['DCC006-DIG', 'ORGANIZACAO DE COMPUTADORES I'], 17: ['OTI071-DIG', 'ORGANIZACAO E TRATAMENTO DA INFORMACAO'],

        18: ['DCC194-DIG', 'INTERACAO HUMANO-COMPUTADOR'], 19: ['CAD004-DIG', 'ADMINISTRACAO DA PRODUCAO'],
        20: ['CIC010-DIG', 'INTRODUÇÃO À CONTABILIDADE'], 21: ['DCC052-DIG', 'PROGRAMACAO MODULAR'],

        22: ['DCC605-DIG', 'SISTEMAS OPERACIONAIS'], 23: ['DCC129-DIG', 'FUNDAMENTOS DA TEORIA DA COMPUTACAO'],
        24: ['CAD153-DIG', 'ADMINISTRACAO DE CUSTOS'], 25: ['DCC603-DIG', 'ENGENHARIA DE SOFTWARE I'],

        26: ['CAD167-DIG', 'ADMINISTRACAO FINANCEIRA'], 27: ['DCC024-DIG', 'LINGUAGENS DE PROGRAMACAO'],
        28: ['DCC072-DIG', 'ENGENHARIA DE SOFTWARE II'],


        29: ['DCC023-DIG', 'REDES DE COMPUTADORES'], 30: ['CAD164-DIG', 'ADMINISTRACAO MERCADOLOGICA'],
        31: ['DCC046-DIG', 'MONOGRAFIA EM SISTEMAS DE INFORMACAO'],

        32: ['DCC606-DIG', 'COMPUTACAO E SOCIEDADE'],
        33: ['DCC073-DIG', 'MONOGRAFIA EM SISTEMAS DE INFORMAÇÃO II']
    };

####################################################### PARÂMETROS #####################################################

    # creditos de cada disciplina
    creditos = [4, 2, 4, 6, 4,    4, 4, 4, 4,    4, 4, 4, 4, 4,    4, 4, 4, 4,    4, 4, 4, 4,    4, 4, 4, 4,    4, 4, 4,    4, 4, 6,  4, 6];

    #índices de retenção (porcentagens) nas respectivas disciplinas
    indicesRetencao = [7, 13, 37, 59, 54,   47, 49, 55, 16,    43, 2, 16, 43, 39,    22, 6, 12, 5,    7, 6, 10, 17,    26, 19, 4, 14,   34, 28, 9,   32, 3, 13,   1, 5];

    # disciplinas e seus respectivos pre-requisitos
    prerequisitos = {7: [3, 4], 6: [2], 8: [0], 15: [0], 19: [0], 20: [0],  12: [6], 16: [11], 24: [20], 28: [25], 26: [24], 33: [31]
                     };

    #disciplinas que devem estar sempre no primeiro período
    disciplinasNivelamento = [0, 1, 2, 3, 4]

    # disciplinas que devem sempre estar no penúltimo período
    disciplinasPenultimoPeriodo = [31]

    # disciplinas que devem sempre estar no último período
    disciplinasUltimoPeriodo = [33]

    # parametros
    quantidadeDisciplinas = len(codigosDisciplinasTraducao);
    quantidadePeriodos = 9;
    quantidadeMinimaDisciplinasPorPeriodo = 2;
    quantidadeMaximaDisciplinasPorPeriodo = 6;
    #Valores retirados do documento de normas da graduação e análise da grade
    cargaMinimaPorPeriodo = 10#extraído da visualização da grade atual(último período com duas disciplinas e carga 10)
    cargaMaximaPorPeriodo = 20#extraído da visualização da grade atual(primeiro período com 5 disciplinas e carga 20)

    #Lower e upper bounds referentes aos critérios
    minCarga = 16
    maxCarga = 20
    minRetencao = 93
    maxRetencao = 753
    minRelacao = 136
    maxRelacao = 2613

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
                                   #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33
    relacaoRelacaoDisciplinas = [  [0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #0
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #1
                                   [0, 0, 0, 0, 0, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #2
                                   [0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #3
                                   [0, 0, 0, 0, 0, 0, 0, 9, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #4
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #5
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0], #6
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #7
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0], #8
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #9
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #10
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #11
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #12
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #13
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #14
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #15
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #16
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #17
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0], #18
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #19
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0], #20
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #21
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0], #22
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #23
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0], #24
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0], #25
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #26
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #27
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #28
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #29
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #30
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9], #31
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #32
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] #33

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
        arquivo = open("resultadoSINUFMG/iteracao "+data_e_hora_em_texto+".txt", "a", encoding='utf-8')
        arquivo.writelines(resultados)
        resultados.clear()
        arquivo.close()

    data_e_hora_atuais_pareto = datetime.now()
    data_e_hora_em_texto_pareto = str(datetime.now())
    data_e_hora_em_texto_pareto = data_e_hora_em_texto_pareto.replace(":", "_")
    data_e_hora_em_texto_pareto = data_e_hora_em_texto_pareto.replace(" ", "_")
    arquivo_pareto = open("resultadoSINUFMG/dadosPareto "+data_e_hora_em_texto_pareto+".txt", "a", encoding='utf-8')
    arquivo_pareto.writelines(resultadosPareto)
    arquivo_pareto.close()

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')
