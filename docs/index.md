# CoSy
<div class="grid" markdown>
![CoSy logo](assets/images/logo.svg){ role="img" }

|                    |                                                                                                                                                                                                                                        |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Package            | [![PyPI - Version](https://img.shields.io/pypi/v/combinatory-synthesizer.svg?style=for-the-badge&logo=pypi&label=&labelColor=grey&logoColor=gold&pypiBaseUrl=https://test.pypi.org)](https://pypi.org/project/combinatory-synthesizer) |
| License            | [![License](https://img.shields.io/github/license/tudo-seal/cosy-draft?style=for-the-badge&color=9E2165&logo=apache&label=&labelColor=grey)](https://opensource.org/licenses/Apache-2.0)                                               |
| Coverage           | [![codecov](https://img.shields.io/codecov/c/github/tudo-seal/cosy-draft?style=for-the-badge&token=40E83ABJV4&logo=codecov&label=&labelColor=grey)](https://codecov.io/github/tudo-seal/cosy-draft)                                    |
| Typed/Type-Checked | [![Checked with mypy](https://img.shields.io/badge/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/tudo-seal/cosy-draft/main/docs/assets/badges/mypy.json)](http://mypy-lang.org/)                                  |
| Linted/Formatted   | [![Checked with Ruff](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&color=4051b5)](https://github.com/astral-sh/ruff)                             |
| Managed with       | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg?style=for-the-badge)](https://hatch.pypa.io/latest/)                                                                                                      |

</div>

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Start synthesizing__

    ---

    Install [`combinatory-synthesizer`](https://pypi.org/project/combinatory-synthesizer/) 
    with [`pip`](https://pypi.org/project/pip/), 
    read an example, 
    and begin synthesizing, all in a few minutes. 

    [:material-arrow-right-box: Quick Start](quick-start.md)  

-   :material-code-tags:{ .lg .middle } __Specify concisely__

    ---

    Use the powerful constraint system of [`CoSy`](https://github.com/tudo-seal/cosy-draft) to generate 
    only the most relevant solutions.  

    [:material-arrow-right-box: Constraints](features/constraints.md) 

-   :material-dna:{ .lg .middle } __Discover advanced features__

    ---

    Learn how users familiar with combinatory logic synthesis can access 
    [`CoSy`](https://github.com/tudo-seal/cosy-draft)'s internals to precisely control synthesis. 

    [:material-arrow-right-box: Advanced](features/advanced.md)

-   :material-school:{ .lg .middle } __Look at examples__

    ---

    Browse a wide selection of examples to kick-start development of your own synthesis projects. 

    [:material-arrow-right-box: Examples](examples/introduction.md)

-   :material-check-bold:{ .lg .middle } __Understand best practices__

    ---

    Understand how to model different types of problems to best capitalize on the performance enhancements of 
    [`CoSy`](https://github.com/tudo-seal/cosy-draft). 

    [:material-arrow-right-box: Best Practice](guidelines/best-practice.md)

-   :material-alert-circle:{ .lg .middle } __Troubleshoot common errors__

    ---

    Find out how to avoid and debug common sources of errors and unexpected behaviour during development.  

    [:material-arrow-right-box: Troubleshoot](guidelines/troubleshoot.md)


</div>

-----

## About
This is just a suggestion text. 

**CoSy** is short for **Co**mbinatory **Sy**nthesizer. 
It is an easy to use, comfortable, even cosy, framework that allows synthesizing target artifacts from modular compontents. 
Due to the domain-agnostic nature of the framework (while implemented in python, arbitrary artifacts can be created), 
it is by-and-large applicable to any use-case that benefits or inherently makes use of modularization. 

## Papers
There is a large body of work concerning combinatory logic synthesis, utilizing CoSy (formerly known as the CLS-framework). 
It has been utilized for robotics, logistics, CAD assemblies, factory planning, and many more. 
An overview over relevant literature, split into applications of CoSy and the theory behind it, is found in the following.
### Applications

### Theory
<div class="grid cards" style="grid-template-columns:repeat(1,minmax(min(100%,16rem),1fr))!important" markdown>

-   :material-book:{ .lg .middle } __[Finite Combinatory Logic with Predicates](https://doi.org/10.4230/LIPIcs.TYPES.2023.2){:target="_blank"}__

    ---

    @theory-dudenhefner-2024
    
 

-   :material-book:{ .lg .middle } __[Finite Combinatory Logic Extended by a Boolean Query Language for Composition Synthesis](https://types2023.webs.upv.es/TYPES2023.pdf){:target="_blank"}__

    ---

    @theory-dudenhefner-2023
    
 

-   :material-book:{ .lg .middle } __[A Type-Theoretic Framework for Software Component Synthesis](http://doi.org/10.17877/DE290R-20320){:target="_blank"}__

    ---

    @theory-bessai-2019
    
 

-   :material-book:{ .lg .middle } __[Algorithmic Aspects of Type-Based Program Synthesis](https://doi.org/10.17877/de290r-20108){:target="_blank"}__

    ---

    @theory-dudenhefner-2019
    
 

-   :material-book:{ .lg .middle } __[CLS-SMT: Bringing Together Combinatory Logic Synthesis and Satisfiability Modulo Theories](https://doi.org/10.4204/EPTCS.301.7){:target="_blank"}__

    ---

    @theory-kallat-2019
    
 

-   :material-book:{ .lg .middle } __[User Support for the Combinator Logic Synthesizer Framework](https://doi.org/10.4204/EPTCS.284.2){:target="_blank"}__

    ---

    @theory-bessai-2018
    
 

-   :material-book:{ .lg .middle } __[Combinatory Synthesis of Classes Using Feature Grammars](https://doi.org/10.1007/978-3-319-28934-2_7){:target="_blank"}__

    ---

    @theory-bessai-2016
    
 

-   :material-book:{ .lg .middle } __[A Long and Winding Road Towards Modular Synthesis](https://doi.org/10.1007/978-3-319-47166-2_21){:target="_blank"}__

    ---

    @theory-heineman-2016
    
 

-   :material-book:{ .lg .middle } __[Mixin Composition Synthesis Based on Intersection Types](https://doi.org/10.4230/LIPIcs.TLCA.2015.76){:target="_blank"}__

    ---

    @theory-bessai-2015
    
 

-   :material-book:{ .lg .middle } __[Towards Migrating Object-Oriented Frameworks to Enable Synthesis of Product Line Members](https://doi.org/10.1145/2791060.2791076){:target="_blank"}__

    ---

    @theory-heineman-2015
    
 

-   :material-book:{ .lg .middle } __[Combinatory Logic Synthesizer](https://doi.org/10.1007/978-3-662-45234-9_3){:target="_blank"}__

    ---

    @theory-bessai-2014
    
 

-   :material-book:{ .lg .middle } __[Staged Composition Synthesis](https://doi.org/10.1007/978-3-642-54833-8_5){:target="_blank"}__

    ---

    @theory-duedder-2014
    
 

-   :material-book:{ .lg .middle } __[Towards Combinatory Logic Synthesis](#){:target="_blank"}__

    ---

    @theory-rehof-2013



-   :material-book:{ .lg .middle } __[Bounded Combinatory Logic](https://doi.org/10.4230/LIPICS.CSL.2012.243){:target="_blank"}__

    ---

    @theory-duedder-2012
    
 

-   :material-book:{ .lg .middle } __[Finite Combinatory Logic with Intersection Types](https://doi.org/10.1007/978-3-642-21691-6_15){:target="_blank"}__

    ---

    @theory-rehof-2011
    
 
</div>
