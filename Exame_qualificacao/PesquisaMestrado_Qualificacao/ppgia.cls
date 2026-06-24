% -------------------------------------------------------------------
%  @LaTeX-class-file{
%     filename        = "ppgia.cls",
%     codetable       = "ISO/ASCII",
%     keywords        = "LaTeX, PUCPR, PPGIa, Thesis, Dissertation",
%     docstring       = "Class for a PPGIa/PUCPR thesis or dissertation.",
%     version         = "v1",
%	  author          = "Jean Paul Barddal"}
% --------------------------------------------------------------------

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ppgia}[PPGIa Dissertation and Thesis Class]

% -- GENERAL SETUP --
% type
\LoadClass[12pt, a4paper, oneside]{book}
% page geometry
\RequirePackage[
  headheight=2cm,
  top=3.5cm,
  bottom=3.5cm,
  footskip=1.5cm,
  footnotesep=1cm,
%  twoside,
  a4paper
]{geometry}
% export in PDF/X, PDF/A, etc...
\RequirePackage{etoolbox}
\RequirePackage{colorprofiles}
\RequirePackage[a-2b,mathxmp]{pdfx}[\today]
% lorem ipsum generator
\RequirePackage{lipsum}
% language, font and encodings
\RequirePackage{newpxtext,newpxmath}
\RequirePackage[T1]{fontenc}
% Idioma português (hifenização e nomes: Capítulo, Figura, Tabela, Sumário...)
\RequirePackage[brazilian]{babel}
%Referências no Formato ABNT:
\RequirePackage[alf,bibjustif,abnt-etal-list=0,abnt-and-type=\&]{abntex2cite}

% -- USEFUL PACKAGES --
% spacings (\onehalfsize, \doublesize)
\RequirePackage{setspace}
% indent first line of paragraph
\RequirePackage{indentfirst}
% captions
\RequirePackage{caption}
\RequirePackage{subcaption}
% footnotes
\RequirePackage{footnote}
\RequirePackage[bottom]{footmisc}
% mathematics
\RequirePackage{amsmath}
% links
\RequirePackage{hyperref}
\RequirePackage{url}
% colors
\RequirePackage{color}
% graphics
\RequirePackage{graphicx}
% algorithms
\RequirePackage{algorithm}
\usepackage{algpseudocode}
% code snippets
\RequirePackage{listings}
% plots, drawings etc...
\RequirePackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta}

% cria float do tipo quadro
\newcounter{quadro}% the counter
\renewcommand*\thequadro{\arabic{chapter}.\arabic{quadro}}% the default format for the counter
\newcommand*\fps@quadro{tbp}% default floating options
\newcommand*\ftype@quadro{4}% float type number, needs to be a power of 2;
\newcommand*\ext@quadro{los}% extension of file for the list of schemes
\newcommand*\fnum@quadro{\quadroname\nobreakspace\thequadro}% used in caption
\newcommand*\quadroname{Quadro}% the name
\newcommand*\listquadroname{Lista de Quadros}% the name of the list
\newenvironment{quadro}{\@float{quadro}}{\end@float}% the environment
\newenvironment{quadro*}{\@dblfloat{quadro}}{\end@dblfloat}% the starred
\newcommand*\listofquadros{% the list of schemes
  \if@twocolumn
    \@restonecoltrue\onecolumn
  \else
    \@restonecolfalse
  \fi
  \chapter*{\listquadroname
    \@mkboth{\MakeUppercase\listquadroname}{\MakeUppercase\listquadroname}}%
  \@starttoc{\ext@quadro}%
  \if@restonecol\twocolumn\fi
  }
\let\l@quadro\l@figure % layout of list is the same as for figures

% -- DEFINITIONS --
\def\idioma#1{\gdef\@idioma{#1}}
\def\universidade#1{\gdef\@universidade{#1}}
\def\programa#1{\gdef\@programa{#1}}
\def\cidade#1{\gdef\@cidade{#1}}

% define tipo do Titulo (mestrado ou doutorado)
\def\tipodocumento#1{
\ifthenelse{\equal{#1}{msc}}{
	\ifthenelse{\equal{\@idioma}{pt-br}}{
		\gdef\@tipotitulocompleto{Mestrado em Informática}
		\gdef\@tipotitulo{Mestre}
		\gdef\@tipodocumentoextenso{Dissertação}
	}{ %en-us
		\gdef\@tipotitulocompleto{Masters in Informatics}
		\gdef\@tipotitulo{Master}
		\gdef\@tipodocumentoextenso{Dissertation}
	}
}{ % phd
	\ifthenelse{\equal{#1}{phd}}{
		\ifthenelse{\equal{\@idioma}{pt-br}}{
			\gdef\@tipotitulocompleto{Doutorado em Informática}
			\gdef\@tipotitulo{Doutor}
			\gdef\@tipodocumentoextenso{Tese}
		}{ %en-us
			\gdef\@tipotitulocompleto{Doctorate in Informatics}
			\gdef\@tipotitulo{Doctor}
			\gdef\@tipodocumentoextenso{Thesis}
		}
	}{ % pdm
		\ifthenelse{\equal{#1}{pdm}}{
			\ifthenelse{\equal{\@idioma}{pt-br}}{
				\gdef\@tipotitulocompleto{Mestrado em Informática}
				\gdef\@tipotitulo{Mestre}
				\gdef\@tipodocumentoextenso{Projeto de Dissertação}
			}{ %en-us
				\gdef\@tipotitulocompleto{Masters in Informatics}
				\gdef\@tipotitulo{Master}
				\gdef\@tipodocumentoextenso{Dissertation Project}
			}
		}{ % pdd
			\ifthenelse{\equal{\@idioma}{pt-br}}{
				\gdef\@tipotitulocompleto{Doutorado em Informática}
				\gdef\@tipotitulo{Doutor}
				\gdef\@tipodocumentoextenso{Projeto de Tese}
			}{ %en-us
				\gdef\@tipotitulocompleto{Doctorate in Informatics}
				\gdef\@tipotitulo{Doctor}
				\gdef\@tipodocumentoextenso{Thesis Project}
			}
		}
	}
}
}

\ifthenelse{\equal{\@idioma}{pt-br}}{
	\gdef\@majorfield{Ciência da Computação}
	\gdef\ALG@name{Algoritmo}
}{ %en-us
	\gdef\@majorfield{Computer Science}
	\gdef\ALG@name{Algorithm}
}

\ifthenelse{\equal{\@idioma}{pt-br}}{
	\renewcommand{\listquadroname}{Lista de Quadros}
}{
	\renewcommand{\listquadroname}{List of Charts}
}

\def\ano#1{\gdef\@ano{#1}}
\def\orientador#1{\gdef\@orientador{#1}}
\def\coorientador#1{\gdef\@coorientador{#1}}
\def\coorientadorUniversidade#1{\gdef\@coorientadorUniversidade{#1}}
\def\@coorientador{\@empty}
\definecolor{PUCPRColor}{RGB}{127, 26, 57}

% -- LINKS SETUP --
\hypersetup{
    colorlinks,
    citecolor=black,
    filecolor=black,
    linkcolor=black,
    urlcolor=black
}

% -- ITEMS AND ENUMARATIONS --
\let\saveditemize=\itemize
\let\savedenditemize=\enditemize
\renewenvironment{itemize}
  {\begin{spacing}{0.5}\saveditemize}
  {\savedenditemize\end{spacing}}

\let\savedenumerate=\enumerate
\let\savedendenumerate=\endenumerate
\renewenvironment{enumerate}
  {\begin{spacing}{0.5}\savedenumerate}
  {\savedendenumerate\end{spacing}}

\let\savedquote\quote
\let\endsavedquote\endquote
\renewenvironment{quote}
  {\itshape\savedquote}
  {\endsavedquote}

% -- HEADERS AND FOOTERS --
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\RequirePackage{scrextend}
\RequirePackage{adjustbox}

\titleformat{\chapter}[display]
  {\Huge}
  {
   \minsizebox{!}{70pt}{\colorbox{PUCPRColor}{\color{white}\thechapter}}
  }
  {1.2ex}
  {}

\titleformat{\section}[hang]
  {\Large}
  {
   \colorbox{PUCPRColor}{\color{white} \thesection}
  }
  {1ex}
  {\scshape}

\titleformat{\subsection}[hang]
  {\large}
  {
   \colorbox{PUCPRColor}{\color{white} \thesubsection}
  }
  {1ex}
  {\scshape}

\titleformat{\subsubsection}[hang]
  {\normalsize}
  {}
  {0ex}
  {\bfseries\scshape}

\renewcommand{\headrulewidth}{0ex}

\newcommand{\setfancyhf} {
  \fancyhf{}
  \fancyhead[RO]{{\footnotesize\leftmark}}
  \fancyhead[LE]{{\footnotesize\rightmark}}
  \fancyfoot[RE, LO]{}
  \fancyfoot[C]{\thepage}
}

% -- Omissor de listagens não usadas e fix de página no Sumário
\usepackage[figure,table,quadro,algorithm,lstlisting]{totalcount}
\newcommand\conditionalLoFigures{%
    \iftotalfigures\clearpage\phantomsection\addcontentsline{toc}{chapter}{\listfigurename}\listoffigures\fi}
\newcommand\conditionalLoTables{%
    \iftotaltables\clearpage\phantomsection\addcontentsline{toc}{chapter}{\listtablename}\listoftables\fi}
\newcommand\conditionalLoQuadros{%
    \iftotaltables\clearpage\phantomsection\addcontentsline{toc}{chapter}{\listquadroname}\listofquadros \fi}
\newcommand\conditionalLoAlgoritmos{%
    \iftotaltables\clearpage\phantomsection\addcontentsline{toc}{chapter}{\listalgorithmname}\listofalgorithms\fi}
\newcommand\conditionalLoCodigos{%
    \iftotallstlistings\clearpage\phantomsection\addcontentsline{toc}{chapter}{\lstlistlistingname}\lstlistoflistings\fi}

% -- FRONTMATTER --
\renewcommand{\frontmatter} {
  \pagenumbering{roman}
  \pagestyle{fancy}
  \maketitle
  \backcover
  
  \setfancyhf
  \setlength{\headwidth}{\textwidth}
  
  \ifthenelse{\equal{\@idioma}{pt-br}}{
    \renewcommand{\contentsname}{Sumário}
    \renewcommand{\listfigurename}{Lista de Figuras}
    \renewcommand{\listtablename}{Lista de Tabelas}
    \renewcommand{\listalgorithmname}{Lista de Algoritmos}
    \renewcommand{\lstlistingname}{Código}
    \renewcommand{\lstlistlistingname}{Lista de Códigos-fonte}
    \def\listacronymname{Lista de Acrônimos}
    \renewcommand{\bibname}{Referências}
    \def\acknowledgmentsname{Agradecimentos}
  }{ %en-us
    \renewcommand{\contentsname}{Contents}
    \renewcommand{\listfigurename}{List of Figures}
    \renewcommand{\listtablename}{List of Tables}
    \renewcommand{\listalgorithmname}{List of Algorithms}
    \renewcommand{\lstlistingname}{Code} 
    \renewcommand{\lstlistlistingname}{List of Codes}
    \def\listacronymname{List of Acronyms}
    \renewcommand{\bibname}{References}
    \def\acknowledgmentsname{Acknowledgements}
  }

  \abstractpage
  
  \tableofcontents

  \conditionalLoFigures
  \conditionalLoTables

  % LISTAS OCULTADAS PARA A QUALIFICAÇÃO (Quadros, Algoritmos, Códigos)
  % \conditionalLoQuadros
  % \conditionalLoAlgoritmos
  % \conditionalLoCodigos

  \acronyms
}

% -- TITLE/COVER (CAPA PRINCIPAL) --
\RequirePackage{watermark}

\renewcommand{\maketitle} {
  \newgeometry{
    top=1.5cm,
    bottom=2cm,
    inner=2cm,
    outer=2cm,
    headheight=4.5cm,
    includehead,
    includefoot,
  }
  \setlength{\headwidth}{\textwidth}
  \thiswatermark{
    \centering
    \put(-400,-650) {
      \includegraphics[width=1.4\linewidth]{template/PUCPR_watermark}
    }
  }
  \cfoot{\normalsize\textsc{\@cidade \ \@ano}}
  \rhead{
    \includegraphics[height=4cm]{template/PUCPR_logo}
  }
  
  \begin{center}
    \vspace*{2cm}
    \normalsize\textsc{
        \@universidade\\
        \@programa \\
    }
  \end{center}
  
  \vspace{\stretch{1.5}}
  
  \begin{center}
     {\Large \textbf{\@title}}\\
     \vspace{\stretch{1}}
     {\large \textbf{\@author}}\\
  \end{center}
  
  \vspace{\stretch{2}}
  
  \begin{center}
     \ifthenelse{\equal{\@idioma}{pt-br}}{Orientador:}{Advisor:} \@orientador \\
  \end{center}

  \clearpage
  \restoregeometry
  \onehalfspacing
}

% -- BACKCOVER (FOLHA DE ROSTO) --
\def\backcover{ 
  \newgeometry{
    top=2cm,
    bottom=2cm,
    inner=2cm,
    outer=2cm,
    headheight=3.5cm,
    includehead,
    includefoot,
  }
  \setlength{\headwidth}{\textwidth}
  \cfoot{\normalsize\textsc{\@cidade \ \@ano}}
  
  \begin{center}
    \vspace*{1cm}
    \normalsize\textbf{\@author}
  \end{center}
  
  \vspace{\stretch{1.5}}
  
  \begin{center}
     {\Large \textbf{\@title}}\\
  \end{center}
  
  \vspace{\stretch{1.5}}
  
  \begin{flushright}
     \begin{minipage}{8cm}
        \small
        \@tipodocumentoextenso\ \ifthenelse{\equal{\@idioma}{pt-br}}{apresentado ao}{presented to the} \@programa\ \ifthenelse{\equal{\@idioma}{pt-br}}{como requisito parcial para obtenção do título de}{as a partial requirement for the title of} \@tipotitulo\ \ifthenelse{\equal{\@idioma}{pt-br}}{em}{in} \@majorfield.\\
        ~\\
        \ifthenelse{\equal{\@idioma}{pt-br}}{Campo de Concentração:}{Field of Concentration:} \@majorfield\\
        ~\\
        \ifthenelse{\equal{\@idioma}{pt-br}}{Orientador:}{Advisor:} \@orientador \\
     \end{minipage}
  \end{flushright}
  
  \vspace{\stretch{2}}
  
  \restoregeometry
  \onehalfspacing
}

% -- FICHA CATALOGRAFICA --
\newcommand{\pathfichacatalografica}{
	\gdef\@pathfichacatalografica{#1}
}
\gdef\@pathfichacatalografica{NONE}

\newcommand{\fichacatalografica}{
    % BLOCO ESVAZIADO E SILENCIADO PARA A QUALIFICAÇÃO
}

% -- DECLARACAO DE DEFESA --
\newcommand{\pathdeclaracaoconclusao}{
	\gdef\@pathdeclaracaoconclusao{#1}
}
\gdef\@pathdeclaracaoconclusao{NONE}

\newcommand\paginadeclaracaoconclusao{
    % BLOCO ESVAZIADO E SILENCIADO PARA A QUALIFICAÇÃO
}

% -- DEDICATION --
\newcommand{\dedicationpage} {
    % BLOCO ESVAZIADO E SILENCIADO PARA A QUALIFICAÇÃO
}

% -- CITATION PAGE --
\newcommand{\citationpage} {
    % BLOCO ESVAZIADO E SILENCIADO PARA A QUALIFICAÇÃO
}

% -- ACRONYMS/ABBREVIATIONS --
\RequirePackage{acronym}
\newcommand{\acronyms}{
  \clearpage
  \phantomsection
  \addcontentsline{toc}{chapter}{\listacronymname}
  \chapter*{\listacronymname}
  \input{frontmatter/glossary}
  \clearpage
}

% -- ACKNOWLEDGMENTS --
\newcommand{\acknowledgments} {
    % BLOCO ESVAZIADO E SILENCIADO PARA A QUALIFICAÇÃO
}

% -- ABSTRACT --
\newenvironment{abstract}{
  \null
  \begin{center}
    \bfseries Abstract
  \end{center}
}

\newenvironment{resumo}{
  \null
  \begin{center}
    \bfseries Resumo
  \end{center}
}

\newenvironment{longcitation}{
	\begin{flushright}
		\footnotesize \itshape
}{
	\end{flushright}
}

\def\palavraschave#1{
	~\\noindent \textbf{Palavras-chave}:~ {#1}}
\def\keywords#1{
	~\\noindent \textbf{Key-words}:~ {#1}}

\newcommand{\abstractpage} {
	\ifthenelse{\equal{\@idioma}{pt-br}}{
		\input{frontmatter/resumo}
		\clearpage
		\input{frontmatter/abstract}
		\clearpage
	}{
		\input{frontmatter/abstract}
		\clearpage
		\input{frontmatter/resumo}
		\clearpage
	}
}

% -- MAIN MATTER --
\renewcommand{\mainmatter} {
  \clearpage
  \setcounter{page}{1}
  \pagenumbering{arabic}
  \setcounter{chapter}{0}
}

% -- BACKMATTER --
\renewcommand{\backmatter}{
  \clearpage
  \phantomsection
  \addcontentsline{toc}{chapter}{\bibname}
  \bibliographystyle{abntex2-alf}
  \bibliography{references.bib}
  \clearpage
  \phantomsection
}

% -- CODE SNIPPETS --
\definecolor{commentsColor}{RGB}{36, 161, 156}
\definecolor{numColor}{RGB}{71, 96, 114}
\definecolor{stringColor}{RGB}{205, 63, 62}
\definecolor{kwColor}{RGB}{248, 6, 204}
\definecolor{bgCodeColor}{RGB}{255, 249, 249}

\lstdefinestyle{codeSnippet} {
  backgroundcolor=\color{bgCodeColor},
  commentstyle=\color{commentsColor},
  keywordstyle=\color{kwColor},
  numberstyle=\tiny\color{numColor},
  stringstyle=\color{stringColor},
  basicstyle=\ttfamily\footnotesize,
  breakatwhitespace=false,
  breaklines=true,
  captionpos=b,
  keepspaces=true,
  numbers=left,
  numbersep=5pt,
  showspaces=false,
  showstringspaces=false,
  showtabs=false,
  tabsize=2
}

\lstset{style=codeSnippet}