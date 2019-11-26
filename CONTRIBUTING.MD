## Contributing

First off, thank you for considering contributing to Leo. It's people
like you that make Leo such a great tool.

### Where do I go from here?

If you've noticed a bug or have a question that doesn't belong on the [mailing
list] or [search the issue tracker] to see if someone else in
the community has already created a ticket. If not, go ahead and [make one][new
issue]!

### Fork & create a branch

If this is something you think you can fix, then [fork Leo] and create
a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-japanese-translations
```

### Get the test suite running

Make sure you're using a recent python version, leo is developed using 3.7

Now run the tests:

```sh
pytest 
```



### Did you find a bug?

* **Ensure the bug was not already reported** by [searching all issues].

* If you're unable to find an open issue addressing the problem,
  [open a new one][new issue]. Be sure to include a **title and clear
  description**, as much relevant information as possible, and a **code sample**
  or an **executable test case** demonstrating the expected behavior that is not
  occurring.

* If possible, use the relevant bug report templates to create the issue.
  Simply copy the content of the appropriate template into a .rb file, make the
  necessary changes to demonstrate the issue, and **paste the content into the
  issue description**:

### Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help;
everyone is a beginner at first :smile_cat:

### Get the style right

we try to enforce a more consistent style and
    follow the Python community guidelines. We currently enforce most of
    [PEP8]

### Add a changelog entry

If your PR includes user-observable changes, you'll be asked to add a changelog
entry following the existing changelog format.

The changelog format is the following:

* One line per PR describing your fix or enhancement.
* Entries end with a dot, followed by "[#pr-number] by [@github-username]".
* Entries are added under the "Unreleased" section at the top of the file, under
  the "Bug Fixes" or "Enhancements" subsection.
* References to github usernames and pull requests use [shortcut reference
  links].
* Your github username reference definition is included in the correct
  alphabetical position at the bottom of the file.

### Make a Pull Request

At this point, you should switch back to your master branch and make sure it's
up to date with Leo's master branch:

```sh
git remote add upstream git@github.com:pivothorizon/leo.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```sh
git checkout 325-add-japanese-translations
git rebase master
git push --set-upstream origin 325-add-japanese-translations
```

Finally, go to GitHub and [make a Pull Request][] :D
### Keeping your Pull Request updated
If a maintainer asks you to "rebase" your PR, they're saying that a lot of code
has changed, and that you need to update your branch so it's easier to merge.

To learn more about rebasing in Git, there are a lot of [good][git rebasing]
[resources][interactive rebase] but here's the suggested workflow:

```sh
git checkout 325-add-japanese-translations
git pull --rebase upstream master
git push --force-with-lease 325-add-japanese-translations
```

### Merging a PR (maintainers only)
A PR can only be merged into master by a maintainer if:

* It is passing all tests.
* It has been approved by at least two maintainers. If it was a maintainer who
  opened the PR, only one extra approval is needed.
* It has no requested changes.
* It is up to date with current master.

Any maintainer is allowed to merge a PR if all of these conditions are
met.

### Shipping a release (maintainers only)
Maintainers need to do the following to push out a release:

* Make sure all pull requests are in and that changelog is current
* If it's not a patch level release, create a stable branch for that release,
  otherwise switch to the stable branch corresponding to the patch release you
  want to ship:

  ```sh
  git checkout master
  git fetch leo
  git rebase leo/master
  # If the release is 2.1.x then this should be: 2-1-stable
  git checkout -b N-N-stable
  git push leo N-N-stable:N-N-stable
  ```



[mailing list]: https://groups.google.com/a/pivothorizon.com/d/forum/leo
[search the issue tracker]: https://github.com/pivothorizon/leo/issues
[new issue]: https://github.com/pivothorizon/leo/issues/new
[fork Leo]: https://help.github.com/articles/fork-a-repo
[searching all issues]: https://github.com/pivothorizon/leo/issues?q=
[shortcut reference links]: https://github.github.com/gfm/#shortcut-reference-link
[make a pull request]: https://help.github.com/articles/creating-a-pull-request
[git rebasing]: http://git-scm.com/book/en/Git-Branching-Rebasing
[interactive rebase]: https://help.github.com/articles/interactive-rebase
[PEP8]: https://www.python.org/dev/peps/pep-0008/
