class DesktopState {
  launcherOpen = $state(false);

  toggleLauncher(): void {
    this.launcherOpen = !this.launcherOpen;
  }

  openLauncher(): void {
    this.launcherOpen = true;
  }

  closeLauncher(): void {
    this.launcherOpen = false;
  }
}

export const desktopState = new DesktopState();
