import subprocess

from tqdm import tqdm

from process_data import main as process_data_main
from process_data import process_source_data


LISTA_MUNICIPIO = [
    'MACEIO', 'SAO JOSE DA TAPERA', 'MATRIZ DE CAMARAGIBE', 'ATALAIA',
    'DELMIRO GOUVEIA', 'ARAPIRACA', 'MARECHAL DEODORO', 'CORURIPE',
    'IGACI', 'PIACABUCU', 'VICOSA', 'SANTANA DO MUNDAU', 'ROTEIRO',
    'MARIBONDO', 'SAO JOSE DA LAJE', 'PARIPUEIRA', 'FEIRA GRANDE',
    'CAPELA', 'GIRAU DO PONCIANO', 'RIO LARGO', 'MURICI',
    'PORTO CALVO', 'PENEDO', 'SAO LUIS DO QUITUNDE', 'TEOTONIO VILELA',
    'AGUA BRANCA', 'PASSO DE CAMARAGIBE', 'PORTO DE PEDRAS',
    'PORTO REAL DO COLEGIO', 'MATA GRANDE', 'PARICONHA', 'CAJUEIRO',
    'SAO SEBASTIAO', 'MARAVILHA', 'TAQUARANA', 'BELEM', 'TRAIPU',
    'PALMEIRA DOS INDIOS', 'COITE DO NOIA', 'JACARE DOS HOMENS',
    'PIRANHAS', 'BARRA DE SAO MIGUEL', 'LAGOA DA CANOA',
    'SAO MIGUEL DOS CAMPOS', 'BATALHA', 'LIMOEIRO DE ANADIA', 'CANAPI',
    'CAMPO ALEGRE', 'SANTANA DO IPANEMA', 'JUNQUEIRO',
    'SAO MIGUEL DOS MILAGRES', 'SATUBA', 'SAO BRAS',
    'UNIAO DOS PALMARES', 'DOIS RIACHOS', 'FLEXEIRAS', 'IBATEGUARA',
    'OLIVENCA', 'SANTA LUZIA DO NORTE', 'PAO DE ACUCAR',
    'JOAQUIM GOMES', 'INHAPI', 'ANADIA', 'COLONIA LEOPOLDINA',
    'SENADOR RUI PALMEIRA', 'PILAR', 'POCO DAS TRINCHEIRAS',
    'MAR VERMELHO', 'CHA PRETA', 'BARRA DE SANTO ANTONIO',
    'MAJOR ISIDORO', 'CRAIBAS', 'BOCA DA MATA', 'BRANQUINHA',
    "OLHO D'AGUA DAS FLORES", 'ESTRELA DE ALAGOAS', 'JARAMATAIA',
    'FELIZ DESERTO', 'CARNEIROS', 'MINADOR DO NEGRAO', 'QUEBRANGULO',
    'MONTEIROPOLIS', 'MARAGOGI', 'MESSIAS', 'JAPARATINGA',
    'JEQUIA DA PRAIA', 'CAMPESTRE', 'NOVO LINO', 'PALESTINA',
    'OURO BRANCO', 'IGREJA NOVA', 'CAMPO GRANDE', "OLHO D'AGUA GRANDE",
    'COQUEIRO SECO', 'JACUIPE', 'CACIMBINHAS', 'BELO MONTE',
    "OLHO D'AGUA DO CASADO", "TANQUE D'ARCA", 'JUNDIA',
    'PAULO JACINTO', 'PINDOBA'
]


if __name__ == "__main__":

    uf = "AL" 

    dataframe = process_source_data(path=f"datasets/source_data/{uf}/dados-vacina.csv")

    dest_vis_dir = f"datasets/{uf}/abandono-atraso-vacinal"

    pbar = tqdm(LISTA_MUNICIPIO)

    for municipio in tqdm(LISTA_MUNICIPIO):
        
        pbar.set_description(f"Salvando dados para {uf} ... {municipio} ")

        process_data_main(uf="AL", municipio=municipio, dataframe=dataframe, dest_vis_dir=dest_vis_dir)
