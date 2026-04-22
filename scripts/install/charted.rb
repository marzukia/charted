class Charted < Formula
  desc "Native SVG chart generation library"
  homepage "https://github.com/marzukia/charted"
  url "https://github.com/marzukia/charted/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "TBD"  # TODO: Update after first release - run `curl -sL URL | sha256sum`
  license "MIT"

  depends_on "python@3.11"

  def install
    system "python3", "-m", "pip", "install", "--no-build-isolation", "-e", "."
    bin.install "bin/charted"
  end

  test do
    system "#{bin}/charted", "--version"
  end
end
