from Foundation import *

def load_sparkle_framework():
    bundlePath = '%s/Sparkle.framework' % Foundation.NSBundle.mainBundle().privateFrameworksPath()
    objc.loadBundle('Sparkle', globals(), bundle_path=bundlePath)

def initialize():
    load_sparkle_framework()
    SUUpdater.sharedUpdater().setAutomaticallyChecksForUpdates_(YES)
