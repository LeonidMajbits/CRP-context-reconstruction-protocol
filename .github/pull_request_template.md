## Summary

Describe the change and the problem it solves.

## Change type

- [ ] Editorial clarification only
- [ ] Example or template change
- [ ] Schema or validation change
- [ ] Protocol-semantic change
- [ ] Compatibility evidence
- [ ] Repository infrastructure

## Contract impact

Explain whether this changes field meaning, mode requirements, canonical syntax,
structured validation, or backward readability. Write `None` when it does not.

## Validation

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python tools/validate_repository.py --root .`
- [ ] New or changed examples have positive and negative coverage
- [ ] Local links and rendered documentation were checked

## Safety and privacy

- [ ] No credentials, personal email addresses, private paths, or private project state
- [ ] No hidden source comments or internal notes
- [ ] Security-sensitive details use GitHub private vulnerability reporting

## Reviewer notes

Call out tradeoffs, unresolved questions, or areas requiring especially careful review.
