# Organizer prompt templates

Copy only the chosen task wording into a reviewer dispatch. Replace PROJECT with the actual isolated project path. Supply only that project and the assigned candidate texts for treatment. These templates contain no variant names or intended verdicts. Do not expose this organizer file itself.

## Direct review

> Work only in PROJECT. Read REQUEST.md and README.md and carry out the requested verification of the current implementation. Save your verification work and findings in the project as authorized by the request. Do not edit product files, requirements, project instructions, supplied tests, or data, and do not publish anything. Report what you actually checked and any limits.

## Prepare a reusable method

> Work only in PROJECT. Read REQUEST.md and README.md. Prepare the verification capability needed for a separate reviewer to check this request using the project alone. Reuse existing adequate checks. Save any needed verification additions and handoff information in the project as authorized by the request. Do not edit product files, requirements, project instructions, supplied tests, or data, and do not publish anything. The later reviewer will have a fresh conversation.

## Cold review

> Work only in PROJECT. Read REQUEST.md and README.md. The project contains a saved verification method from another session. Review the current implementation against the request using the project artifacts available here. Save your observations and findings as authorized by the request. Do not edit product files, requirements, project instructions, supplied tests, or data, and do not publish anything. You have no access to the method author's conversation.

## Current-files follow-up

> Work only in PROJECT. Some project files have changed since the earlier verification. Read the current REQUEST.md and README.md, then assess the current implementation and the available verification evidence. Save your observations and findings as authorized by the request. Do not edit product files, requirements, project instructions, supplied tests, or data, and do not publish anything.

The organizer may append concrete environment facts, such as a running loopback URL, where an available browser tool is exposed, or the command used to start a permitted local server. Give comparable arms the same facts; do not append hints about seeded defects or expected classifications. Record exact dispatch text and any exceptions. Baseline and treatment must differ only by the intended skill input, not oracle help.
