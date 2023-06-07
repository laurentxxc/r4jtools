# Purpose
Python script `r4jtools.py` allows to export [R4J](https://marketplace.atlassian.com/apps/1213064/r4j-requirements-management-for-jira?tab=overview&hosting=cloud) requirements in a word documentation.

# Dependencies
`r4jtools.py` mainly depends on following:

* [R4J REST 2.0 API](https://easesolutions.atlassian.net/wiki/spaces/REQ4J/pages/1473937542/REST+API+2.0+Reference)
* [JIRA REST API](https://developer.atlassian.com/server/jira/platform/rest-apis/)
* [python-docx api](https://python-docx.readthedocs.io/en/latest/)

# Input & Configuration
`r4jtools.py` requires 2 main inputs:

1. Main Configuration file
2. Word template

## Main configuration file
`r4jtools.py`main configuration file is yaml format and must include the following informations:

* Word file output name
* Word file template used to inject requirement
* R4J Server address
* R4J project key

A configuration template example is available in [config.yaml](input_samples/config.yaml)

## Word template
Word template allow to contain generic informations about a specific project that generally are not described in the requirement database. Such document also define presentation style and look for external publication.
When exporting requirements, `r4jtools.py` will first instanciate the word template in a new document with appropriate name
Requirements from the configured project will be then exported at a specific insertion point defined by text `<Requirements>` with format style name `Insertion Point`.
Requirements will be exported, grouped and ordered following R4J project database folder structure and using following word format styles:

* `Heading 2`..`Heading n`: Heading style used to format R4J folder name repesenting a dedicated set of requirements
* `Requirement_list`: Table style used to format all details of a each requirement in one dedicated table
* `Requirement Title`: Paragraph style used to format requirement title
* `Requirement`: Paragraph style used to format other requirement informations (e.g. description, dependencies)

A Word template example is available in [TechRequirementTemplate.docx](inputs_amples/TechRequirementTemplate.docx)

# TODOS
Following features to be added:

* Addition requirement info
    * Jira link
    * Req dependencies
    * others Jira fields
* Particular case for requirement with build field (comment, image or table)
* Filter req (with jql)
* Add traceability matrix
* ...
