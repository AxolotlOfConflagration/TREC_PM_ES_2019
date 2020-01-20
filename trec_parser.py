from ftplib import FTP
from pathlib import Path
from io import BytesIO
from gzip import GzipFile
from collections import namedtuple
from enum import Enum
import json
import re
from tqdm import tqdm

def download_files(n=10, offset=0, callback=None):
    """
    Downloads n first files from the FTP as generator.
    It yields values as tuple (file_name, bytes_io)
    """
    ftp = FTP('ftp.ncbi.nlm.nih.gov')
    ftp.login()
    ftp.cwd('pubmed/baseline/')

    file_names = [name for name in ftp.nlst() if name.endswith(".gz")]
    file_names = sorted(file_names)[offset:n]

    for file_name in file_names:
        buffer = BytesIO()

        ftp.retrbinary(f'RETR {file_name}', buffer.write)
        buffer.seek(0)

        yield (file_name, buffer)

        if not buffer.closed:
            buffer.close()
        
    ftp.quit()

def unpack(iterable):
    """
    Unpacks the provided iterable of items in format (file_name, file_handler).
    It yields the content of the file as tuple (file_name, string_content).
    """
    for file_name, file in iterable:
        with GzipFile(fileobj=file) as gfile:
            binary_content = gfile.read()
            content = binary_content.decode('utf-8') 
            file_name = file_name[:-3]
            yield file_name, content

def file_sink(iterable, output_dir):
    """
    Saves the iterator content in form (file_name, string) 
    under output_dir with given file_name
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for file_name, value in iterable:
        output_file_name = output_dir.joinpath(file_name) 
        with open(output_file_name, 'w') as file:
            file.write(value)

class Document:
    def __init__(self):
        self.doc_id = ''
        self.abstract = ''
        self.title = ''
        self.mesh_terms = []
        self.substances = []
    
    def to_dict(self):
        return {
            "DocID": self.doc_id,
            "ArticleTitle": self.title,
            "AbstractText": self.abstract,
            "MeshTerms": self.mesh_terms,
            "SubstanceNames": self.substances
        }

    def __repr__(self):
        fields = str(self.__dict__)[1:-1]
        return f'Document({fields})'

    def to_json(self):
        return json.dumps(self.to_dict())
    

class State(Enum):
    IDLE = 0,
    ABSTRACT = 1,
    TITLE = 2,
    MESH = 3,
    SUBSTANCES = 4,
    CHEMICALS = 5

class DocumentParser:
    def __init__(self):
        self.documents = []
    
    def parse(self, file_name = None, file_obj = None):
        if file_obj is not None:
            self._process_file(file_obj)
        else:
            with tqdm(open(file_name)) as file:
                self._process_file(file)
    
    def save_documents(self, file_path):
        file_path = Path(file_path)
        file_path.parent.mkdir(exist_ok=True, parents=True)

        docs = [doc.to_dict() for doc in self.documents]
        with open(file_path, 'w') as file:
            json.dump(docs, file)

    def as_jsons(self):
        docs = [doc.to_dict() for doc in self.documents]
        return json.dumps(docs)

    def _process_file(self, file):
        document: Document = None

        for line in file:
            line: str = line.strip()
            if line == "<PubmedArticle>":
                document = Document()
            elif line == "</PubmedArticle>":
                self.documents.append(document)
                document = None
            elif line.startswith('<ArticleId IdType="pubmed">'):
                result = re.search(r'<ArticleId IdType="pubmed">(?P<doc_id>\d+)</ArticleId>', line)
                document.doc_id = result.group('doc_id')
            elif line.startswith('<ArticleTitle>'):
                result = re.search(r'<ArticleTitle>(?P<title>.+)</ArticleTitle>', line)
                document.title = result.group('title')
            elif line.startswith('<AbstractText'):
                result = re.search(r'<AbstractText.*>(?P<abstract>.+)</AbstractText>', line)
                document.abstract = result.group('abstract')
            elif line.startswith('<NameOfSubstance'):
                result = re.search(r'<NameOfSubstance.*>(?P<substance>.+)</NameOfSubstance>', line)
                document.substances.append(result.group('substance'))
            elif line.startswith('<DescriptorName'):
                result = re.search(r'<DescriptorName.*>(?P<mesh_term>.+)</DescriptorName>', line)
                document.mesh_terms.append(result.group('mesh_term'))



if __name__ == "__main__":
    # file_sink(unpack(download_files()), './results/xmls')

    parser = DocumentParser()
    parser.parse('results/xmls/pubmed20n0001.xml')
    parser.save_documents('results/jsons/pubmed20n0001.json')

