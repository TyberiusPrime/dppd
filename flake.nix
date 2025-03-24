{
  description = "dppd development falke";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
    uv2nix.url = "github:/adisbladis/uv2nix";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-nix.url = "github:/nix-community/pyproject.nix";
    pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
    uv2nix.inputs.pyproject-nix.follows = "pyproject-nix";
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    #uv2nix_hammer_overrides.url = "github:TyberiusPrime/uv2nix_hammer_overrides";
  };
  outputs = {
    nixpkgs,
    uv2nix,
    pyproject-build-systems,
    #uv2nix_hammer_overrides,
    ...
  }: let
    pyproject-nix = uv2nix.inputs.pyproject-nix;
    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};

    pkgs = import nixpkgs {
      system = "x86_64-linux";
      config.allowUnfree = true;
    };

    # Generate overlay
    overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel";
    };
    pyprojectOverrides = final: prev: {};
    #pyprojectOverrides = final: prev: {} ;
    interpreter = pkgs.python312;
    spec = {
      dppd = ["dev"];
    };

    # Construct package set
    pythonSet' =
      (pkgs.callPackage pyproject-nix.build.packages {
        python = interpreter;
      })
      .overrideScope
      (
        pkgs.lib.composeManyExtensions [
          pyproject-build-systems.overlays.default
          overlay
          pyprojectOverrides
        ]
      );

    # Override host packages with build fixups
    pythonSet = pythonSet'.pythonPkgsHostHost.overrideScope pyprojectOverrides;
    virtualEnv = pythonSet.mkVirtualEnv "dppd-ven" spec;
  in {
    #packages.x86_64-linux.default = defaultPackage;
    devShell.x86_64-linux = pkgs.mkShell {
      packages = [
        virtualEnv
      ];
      shellHook = ''
        # Undo dependency propagation by nixpkgs.
        unset PYTHONPATH
      '';
    };
  };
}
