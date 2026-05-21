class DonghuaCli < Formula
  include Language::Python::Virtualenv

  desc "Wuxia-themed terminal client for streaming Chinese animation"
  homepage "https://github.com/Thanukamax/donghua-cli"
  # Update URL and sha256 on each release
  url "https://files.pythonhosted.org/packages/source/d/donghua-cli/donghua_cli-3.2.0.tar.gz"
  sha256 "UPDATE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "python@3.12"
  depends_on "mpv" => :recommended

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "donghua-cli", shell_output("#{bin}/donghua --version")
  end
end
