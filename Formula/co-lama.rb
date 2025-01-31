class CoLama < Formula
  include Language::Python::Virtualenv

  desc "Docker container manager using Colima"
  homepage "https://github.com/lvonsydow/co-lama"
  url "https://github.com/lvonsydow/co-lama/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "da75081f00f2ddd2abd330e17c7798ab1cecf6330060a62d8e5dd9807d926825"
  license "MIT"

  depends_on "python@3.11"
  depends_on "colima"

  resource "pyside6" do
    url "https://files.pythonhosted.org/packages/ba/9a/3483d05305701ba810192572cee5977ff884c033a1b8f96ab9582d81ccd4/PySide6-6.6.3.1-cp38-abi3-macosx_11_0_universal2.whl"
    sha256 "3d2ebb08a7744b59e1270e57f264a9ef5b45fccdc0328a9aeb50d890d6b3f4f2"
  end

  resource "pyside6-addons" do
    url "https://files.pythonhosted.org/packages/51/3e/b77d2b9a1efcb5c90a2df4f51eb10bce45b3787c4fa16b69c599fd6620b9/PySide6_Addons-6.6.3.1-cp38-abi3-manylinux_2_31_aarch64.whl"
    sha256 "f7acd26fe8e1a745ef0be66b49ee49ee8ae50c2a2855d9792db262ebc7916d98"
  end

  resource "pyside6-essentials" do
    url "https://files.pythonhosted.org/packages/af/90/3164ace42cb80ed55642e965934133d0c49bfa3ea79e43631dd331cdc866/PySide6_Essentials-6.6.3.1-cp38-abi3-win_amd64.whl"
    sha256 "d993989a10725c856f5b07f25e0664c5059daa92c259549c9df0972b5b0c7935"
  end

  resource "shiboken6" do
    url "https://files.pythonhosted.org/packages/14/60/dc79d4ea59ed1ebe6062c5db972b31d489ea84315dcf3bd58a2a741c73b3/shiboken6-6.6.3.1-cp38-abi3-manylinux_2_28_x86_64.whl"
    sha256 "35936f06257e5c37ae8993da0cb5a528e5db3ea1fc2bb6b12cdf899a11510966"
  end

  resource "docker" do
    url "https://files.pythonhosted.org/packages/source/d/docker/docker-7.0.0.tar.gz"
    sha256 "323736fb92cd9418fc5e7133bc953e11a9da04f4483f828b527db553f1e7e5a3"
  end

  resource "qasync" do
    url "https://files.pythonhosted.org/packages/source/q/qasync/qasync-0.27.1.tar.gz"
    sha256 "eec7dd1d1e88d0ce5a1b3f0c68f3efc6e9c2a3df0f8e8c7aa6c45a83f42f5a9b"
  end

  def install
    virtualenv_install_with_resources
  end

  def caveats
    <<~EOS
      To use Co-lama, you need to have Colima installed and running.
      You can start Colima with:
        colima start
    EOS
  end

  test do
    system bin/"colama", "--version"
  end
end
