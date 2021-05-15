# Observações para considerar no tratamento:

- aplicar str.split() em todos os campos de string para remover espaços no
  início ou fim das strings;
- não considerar a coluna `vacina_fabricante_nome` ao remover duplicados, pois
  existem, por exemplo, Coronavac registrada com fabricante FUNDACAO BUTANTAN
  e SERUM INSTITUTE OF INDIA LTD;
- não considerar o CEP ao remover duplicados, pois existem registros de um
  mesmo `paciente_id` com CEP e sem CEP;
