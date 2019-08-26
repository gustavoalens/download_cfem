from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webdriver import WebDriver
import pandas as pd


def td2float(td):
    """Extrai o valor que está inserido na célula de tabela em html e converte para float

    :param td: Célula da tabela, referente a tag <td></td>
    :type td: WebDriver
    :return: Valor inserido na celula da tabela em float
    :rtype: float
    """
    val = td.get_attribute('innerHTML').strip(' \n\t')
    if val == '&nbsp;':
        return 0.0
    val = val.replace('.', '')
    return float(val.replace(',', '.'))


def extrai_dados(path_driver, sigla_uf, ano_i, ano_f, file_save, sep=';', decimal=','):
    """Rotina de extração dos dados de arrecadação por cidade e substrato

    :param path_driver: diretório do arquivo chromedriver (ex: /path/to/chromedriver)
    :type path_driver: str
    :param sigla_uf: sigla do estado que irá ser extraído os dados (ex: MT)
    :type sigla_uf: str
    :param ano_i: ano inicial da pesquisa
    :type ano_i: int
    :param ano_f: ano final da pesquisa
    :type ano_f: int
    :param file_save: diretório e nome do arquivo que irá ser salvo o csv dos dados extraído (ex: /path/to/filename)
    :type file_save: str
    :param sep: carácter que irá separar cada item no arquivo csv
    :type sep: str
    :param decimal: carácter que separará os valores decimais
    :type decimal: str
    :return: salva arquivo e retorna o DataFrame dos dados extraídos
    :rtype: pd.DataFrame
    """

    # criando dataframe pandas
    arr = pd.DataFrame(columns=['cod_mun', 'nome_mun', 'subs', 'jan', 'fev',
                                'mar', 'abr', 'mai', 'jun', 'jul', 'ago',
                                'set', 'out', 'nov', 'dez', 'total', 'ano'])

    # iniciando a web
    dr = webdriver.Chrome(path_driver)

    # abrindo a página
    dr.get('https://sistemas.dnpm.gov.br/arrecadacao/extra/Relatorios/arrecadacao_cfem_substancia.aspx')

    for a in range(ano_i, ano_f + 1):
        # selecionando o campos selects
        ano = Select(dr.find_element_by_name('ctl00$ContentPlaceHolder1$nu_ano'))

        # selecionando por valor o ano
        ano.select_by_value(str(a))  # usar valor do ano (convertendo para string)

        # selcionando somente mt
        estado = Select(dr.find_element_by_name('ctl00$ContentPlaceHolder1$unfe_sigla_uf'))
        estado.select_by_value(sigla_uf)

        mun_opc = Select(dr.find_element_by_name('ctl00$ContentPlaceHolder1$muni_cod_municipio')).options
        cods = list()
        for op in mun_opc[1:]:
            print(op)
            cods.append(int(op.get_attribute('value')))

        for cod in cods:
            # selecionando a cidade por index (inicia em 2)
            municipio = Select(dr.find_element_by_name('ctl00$ContentPlaceHolder1$muni_cod_municipio'))
            municipio.select_by_value(str(cod))
            nome_mun = municipio.first_selected_option.get_attribute('innerHTML')

            # encontrando o botão e simulando click
            gera = dr.find_element_by_name('ctl00$ContentPlaceHolder1$btnGera')
            gera.click()

            # tabela resultado da pesquisa (submit)
            table = dr.find_element_by_class_name('tabelaRelatorio')

            # cria uma lista com cada linha da tabela resultante
            trs = table.find_elements_by_tag_name('tr')

            # acessando a primeira linha após o head até o penultimo (ultima linha é inutil)
            print('#' * 30)
            print(f'Escavando os dados do município {nome_mun} do ano de {a}')
            print('#' * 30)
            dados = list()
            for tr in trs[1:-1]:
                tds = tr.find_elements_by_tag_name('td')
                dados.append(list())
                dados[-1].append(cod)
                dados[-1].append(nome_mun)
                dados[-1].append(tds[1].get_attribute('innerHTML').strip(' \n\t'))
                for td in tds[2:14]:
                    dados[-1].append(td2float(td))
                dados[-1].append(td2float(tds[14]))
                dados[-1].append(a)
                aux = pd.DataFrame(dados, columns=arr.columns)
                arr = arr.append(aux, ignore_index=True)

    arr.to_csv(f'{file_save}.csv', index=False, sep=sep, decimal=decimal)
    return arr


if __name__ == '__main__':
    # ToDo: Substituir os respectivos valores
    df = extrai_dados('/path/to/chromedriver', 'UF', 2010, 2018,
                      '/path/to/filename')  # irá salvar no diretório e retornar o dataframe Pandas

