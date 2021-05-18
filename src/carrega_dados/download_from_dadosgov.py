import os
from datetime import datetime, date, timedelta
from lxml import html 
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import re
from glob import glob
import locale
locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
 
def find_last_date(output_folder):
    filescsv = glob(output_folder + '/*.csv')
    fileszip = glob(output_folder + '/*.zip')
    filesxz = glob(output_folder + '/*.xz')
    filesbz2 = glob(output_folder + '/*.bz2')
    files = filescsv + fileszip + filesxz + filesbz2
    date_max = date(year=2020, month=1, day=1)
    for f in files:
        g = re.match(r'.*(\d\d\d\d_\d\d_\d\d).*', os.path.basename(f))
        if g:
            data = datetime.strptime(g.groups()[0], "%Y_%m_%d").date()
            date_max = max(data, date_max)
    return date_max

def check_new_update_date(index_page_address, data):
    page = requests.get(index_page_address, verify=False, timeout=10)
    tree = html.fromstring(page.content)
    data_str = tree.xpath('//*[@id="content"]/div[3]/div/section/div/table/tbody/tr[1]/td')[0].text
    dt = datetime.strptime(data_str, '%d/%B/%Y').date()
    if dt > data:
        return dt
    return False

def get_file(download_address, output_file):
    s = requests.Session()
    retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])

    s.mount('https://', HTTPAdapter(max_retries=retries))

    r = s.get(download_address, verify=False, allow_redirects=True, timeout=10)

#     r = requests.get(download_address, verify=False, allow_redirects=True, timeout=10)
    open(output_file, 'wb').write(r.content)

def get_resource_names(index_page_address):
    page = requests.get(index_page_address, verify=False, timeout=10)
    tree = html.fromstring(page.content)
    res = tree.xpath('//a/@href')
    resources = {}
    for r in res:
        if r is None: break
#         print(r)
        g = re.match(r'.*uf%3D(.*)/part.*', r.strip('\n'))
        if g:
            resources[g.groups()[0]] = r
    return resources

if __name__ == '__main__':
    index_page_address = 'https://opendatasus.saude.gov.br/dataset/covid-19-vacinacao/resource/ef3bd0b8-b605-474b-9ae5-c97390c197a8'
    # download_address = "https://s3-sa-east-1.amazonaws.com/ckan.saude.gov.br/dados-{estado}.csv"
    download_address = "https://s3-sa-east-1.amazonaws.com/ckan.saude.gov.br/PNI/vacina/uf/2021-05-02/uf%3D{estado}/part-00000-2a9d0e2a-e780-4468-b4f8-7e0a1a01b3de.c000.csv"
#     https://s3-sa-east-1.amazonaws.com/ckan.saude.gov.br/PNI/vacina/uf/2021-05-16/uf%3DGO/part-00000-f3588c19-4ab8-42b1-86e7-7ff9ab4ff9b2.c000.csv

    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../datasets/raw')
    gitUpdate = False

    #estados = ["ac", "al", "am", "ap", "ba", "ce", "df", "es", "go",
    #        "ma", "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr", "rj", "rn",
    #        "ro", "rr", "rs", "sc", "se", "sp", "to"]
    res = get_resource_names(index_page_address)
    print(res)
    last_date = find_last_date(output_folder)
    data = check_new_update_date(index_page_address, last_date)
    if data:
        print("Downloading new open datasus database...")
        new_files = []
        for estado, link in res.items():
            print('Baixando ', estado, link)
            output_file = output_folder + '/open-datasus_{estado}-{data}.csv'.format(estado=estado,
                    data=data.strftime("%Y_%m_%d"))
#            get_file(download_address.format(estado=estado), output_file)
            get_file(link, output_file)
            # os.system("bzip2 " + output_file)
            # new_files.append(output_file + '.bz2')
            new_files.append(output_file)
        # add to git and let the other robots work
        if gitUpdate:
            os.system("cd {folder} && git pull --ff-only".format(
                folder=output_folder))
            os.system('''cd {folder} &&
                   git add {outfiles} &&
                   git commit -m "[auto] bases esus-ve de hoje" &&
                   git push'''.format(folder=output_folder,
                                    outfiles=' '.join(new_files)))

