Automated GUI Testing for Miro Video Converter 3
================================================

The whole thing is setup to use [project sikuli](http://sikuli.org), the GUI test tool in combination
with [lettuce](http://lettuce.it) to describe the features and drive the tests.

This directory is setup as follows:
- features
 - *.feature
 - terrain
  - Images *shared image files*
  - Images_osx
  - Images_win
  - Images_lin
  - steps *each step in the .feature file is mapped in here*
  - mvc *modules in the steps directory call mvc modules that are driven by sikuli*


