# Observações para considerar no tratamento:

- aplicar str.trim() em todos os campos de string para remover espaços no
  início ou fim das strings;
- não considerar a coluna `vacina_fabricante_nome` ao remover duplicados, pois
  existem, por exemplo, Coronavac registrada com fabricante FUNDACAO BUTANTAN
  e SERUM INSTITUTE OF INDIA LTD;
- não considerar o CEP ao remover duplicados, pois existem registros de um
  mesmo `paciente_id` com CEP e sem CEP;
- Considerar os registros que só tem segunda dose como sendo aplicação de
  primeira dose. Salvar somente os registros que mudaram em um  dataset por
  municipio, que será futuramente usado pelos municipios.
- Trocar os registros onde a segunda dose vem antes ou na mesma data da
  primeira, colocando a aplicação da segunda dose como sendo aplicação da
  primeira dose e vice versa. Salvar somente os registros que mudaram em um
  dataset por municipio, que será futuramente usado pelos municipios.
- Se o nome da vacina na primeira dose é diferente da segunda, considerar na
  segunda aplicação o nome da primeira aplicação.  Salvar somente os registros
  que mudaram em um  dataset por municipio, que será futuramente usado pelos
  municipios.
- Se não houver data da aplicação, inserir a data da informação ao sistema do
  SUS. Salvar somente os registros que mudaram em um  dataset por municipio,
  que será futuramente usado pelos municipios.
- Salvar os registros dos duplicados que foram excluidos em um  dataset por
  municipio, que será futuramente usado pelos municipios.

# Questões para resolver

- O que fazer com datas de vacina anteriores ao início da vacinação ou no
  futuro?
- O que fazer com pacientes com data de nascimento muito antiga? Definir data
  muito antiga.
