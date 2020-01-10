# Enable hardening in RHEL 7
%global _hardened_build 1

%global glib2_version 2.45.8
%global libappstream_version 0.7.4
%global libgusb_version 0.2.9
%global libsoup_version 2.51.92
%global systemd_version 219
%global json_glib_version 1.1.1

%global enable_tests 0
%global enable_dummy 0

# fwupdate is only available on these arches
%ifarch x86_64 aarch64
%global have_uefi 1
%endif

# libsmbios is only available on x86, and fwupdate is available on just x86_64
%ifarch x86_64
%global have_dell 1
%endif

# valgrind is not available on s390
%ifarch x86_64 aarch64
%global have_valgrind 1
%endif

Summary:   Firmware update daemon
Name:      fwupd
Version:   1.0.8
Release:   4%{?dist}
License:   LGPLv2+
URL:       https://github.com/hughsie/fwupd
Source0:   http://people.freedesktop.org/~hughsient/releases/%{name}-%{version}.tar.xz

# neuter the LVFS
Patch2:    0001-Do-not-use-the-LVFS.patch
Patch3:    0002-Do-not-use-Python-version-3.patch

# backport
Patch6:    0001-Allow-running-on-an-older-systemd.patch

BuildRequires: gettext
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: libappstream-glib-devel >= %{libappstream_version}
BuildRequires: libgudev1-devel
BuildRequires: libgusb-devel >= %{libgusb_version}
BuildRequires: libsoup-devel >= %{libsoup_version}
BuildRequires: polkit-devel >= 0.103
BuildRequires: sqlite-devel
BuildRequires: gpgme-devel
BuildRequires: systemd >= %{systemd_version}
BuildRequires: libarchive-devel
BuildRequires: gobject-introspection-devel
BuildRequires: gcab
%if 0%{?have_valgrind}
BuildRequires: valgrind
BuildRequires: valgrind-devel
%endif
BuildRequires: elfutils-libelf-devel
BuildRequires: gtk-doc
BuildRequires: libuuid-devel
BuildRequires: meson
BuildRequires: help2man
BuildRequires: json-glib-devel >= %{json_glib_version}
BuildRequires: vala

%if 0%{?have_dell}
BuildRequires: efivar-devel
BuildRequires: libsmbios-devel >= 2.3.0
%endif

%if 0%{?have_uefi}
BuildRequires: fwupdate-devel >= 10
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

Requires: glib2%{?_isa} >= %{glib2_version}
Requires: libappstream-glib%{?_isa} >= %{libappstream_version}
Requires: libgusb%{?_isa} >= %{libgusb_version}
Requires: libsoup%{?_isa} >= %{libsoup_version}

Obsoletes: fwupd-sign < 0.1.6
Obsoletes: libebitdo < 0.7.5-3

%description
fwupd is a daemon to allow session software to update device firmware.

%package devel
Summary: Development package for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: libebitdo-devel < 0.7.5-3
Obsoletes: libdfu-devel < 1.0.0

%description devel
Files for development with %{name}.

%prep
%setup -q
%patch2 -p1 -b .no-lvfs
%patch3 -p1 -b .no-python3
%patch6 -p1 -b .old-systemd

%build

%meson \
    -Dpkcs7=false \
    -Dgtkdoc=true \
%if 0%{?enable_tests}
    -Dtests=true \
%else
    -Dtests=false \
%endif
%if 0%{?enable_dummy}
    -Dplugin_dummy=true \
%else
    -Dplugin_dummy=false \
%endif
    -Dplugin_thunderbolt=true \
%if 0%{?have_uefi}
    -Dplugin_uefi=true \
    -Dplugin_uefi_labels=false \
%else
    -Dplugin_uefi=false \
    -Dplugin_uefi_labels=false \
%endif
%if 0%{?have_dell}
    -Dplugin_dell=true \
    -Dplugin_synaptics=true \
%else
    -Dplugin_dell=false \
    -Dplugin_synaptics=false \
%endif
    -Dman=true

%meson_build

%if 0%{?enable_tests}
%check
%meson_test
%endif

%install
%meson_install

mkdir -p --mode=0700 $RPM_BUILD_ROOT%{_localstatedir}/lib/fwupd/gnupg

%find_lang %{name}

%post
/sbin/ldconfig
%systemd_post fwupd.service

%preun
%systemd_preun fwupd.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart fwupd.service

%files -f %{name}.lang
%doc README.md AUTHORS NEWS
%license COPYING
%config(noreplace)%{_sysconfdir}/fwupd/daemon.conf
%if 0%{?have_uefi}
%config(noreplace)%{_sysconfdir}/fwupd/uefi.conf
%endif
%dir %{_libexecdir}/fwupd
%{_libexecdir}/fwupd/fwupd
%{_libexecdir}/fwupd/fwupdtool
%{_bindir}/dfu-tool
%{_bindir}/fwupdmgr
%dir %{_sysconfdir}/fwupd
%dir %{_sysconfdir}/fwupd/remotes.d
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/fwupd.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/lvfs.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/lvfs-testing.conf
%config(noreplace)%{_sysconfdir}/fwupd/remotes.d/vendor.conf
%config(noreplace)%{_sysconfdir}/pki/fwupd
%{_sysconfdir}/pki/fwupd-metadata
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.fwupd.conf
%{_datadir}/fwupd/metainfo/org.freedesktop.fwupd*.metainfo.xml
%{_datadir}/fwupd/remotes.d/fwupd/metadata.xml
%{_datadir}/fwupd/remotes.d/vendor/firmware/README.md
%{_datadir}/dbus-1/interfaces/org.freedesktop.fwupd.xml
%{_datadir}/polkit-1/actions/org.freedesktop.fwupd.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.fwupd.rules
%{_datadir}/dbus-1/system-services/org.freedesktop.fwupd.service
%{_datadir}/man/man1/dfu-tool.1.gz
%{_datadir}/man/man1/fwupdmgr.1.gz
%{_datadir}/metainfo/org.freedesktop.fwupd.metainfo.xml
%{_datadir}/fwupd/firmware-packager
%{_unitdir}/fwupd-offline-update.service
%{_unitdir}/fwupd.service
%{_unitdir}/system-update.target.wants/
%dir %{_localstatedir}/lib/fwupd
%dir %{_datadir}/fwupd/quirks.d
%{_datadir}/fwupd/quirks.d/*.quirk
%{_localstatedir}/lib/fwupd/builder/README.md
%{_libdir}/libfwupd*.so.*
%{_libdir}/girepository-1.0/Fwupd-2.0.typelib
/usr/lib/udev/rules.d/*.rules
%dir %{_libdir}/fwupd-plugins-3
%{_libdir}/fwupd-plugins-3/libfu_plugin_altos.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_amt.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_colorhug.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_csr.so
%if 0%{?have_dell}
%{_libdir}/fwupd-plugins-3/libfu_plugin_dell.so
%endif
%{_libdir}/fwupd-plugins-3/libfu_plugin_dfu.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_ebitdo.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_nitrokey.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_steelseries.so
%if 0%{?have_dell}
%{_libdir}/fwupd-plugins-3/libfu_plugin_synapticsmst.so
%endif
%if 0%{?enable_dummy}
%{_libdir}/fwupd-plugins-3/libfu_plugin_test.so
%endif
%{_libdir}/fwupd-plugins-3/libfu_plugin_thunderbolt.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_thunderbolt_power.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_udev.so
%if 0%{?have_uefi}
%{_libdir}/fwupd-plugins-3/libfu_plugin_uefi.so
%endif
%{_libdir}/fwupd-plugins-3/libfu_plugin_unifying.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_upower.so
%{_libdir}/fwupd-plugins-3/libfu_plugin_wacomhid.so
%ghost %{_localstatedir}/lib/fwupd/gnupg

%files devel
%{_datadir}/gir-1.0/Fwupd-2.0.gir
%{_datadir}/gtk-doc/html/libfwupd
%{_datadir}/vala/vapi
%{_includedir}/fwupd-1
%{_libdir}/libfwupd*.so
%{_libdir}/pkgconfig/fwupd.pc

%changelog
* Wed Sep 05 2018 Kalev Lember <klember@redhat.com> 1.0.8-4
- Build with full hardening enabled
- Resolves: #1616185

* Mon Jul 16 2018 Richard Hughes <rhughes@redhat.com> 1.0.8-3
- Backport a fix to allow properly running on older systemd versions.
- Resolves: #1601550

* Thu Jun 14 2018 Richard Hughes <rhughes@redhat.com> 1.0.8-2
- Build against the new libfwupdate
- Resolves: #1570028

* Fri Jun 08 2018 Richard Hughes <rhughes@redhat.com> 1.0.8-1
- New upstream release
- Resolves: #1570028

* Mon Jan 08 2018 Richard Hughes <richard@hughsie.com> 1.0.1-4
- Enable the libsmbios dependency to get the Dell plugin
- Resolves: #1420913

* Thu Nov 23 2017 Richard Hughes <richard@hughsie.com> 1.0.1-3
- Remove the runtime dep on bubblewrap.
- Resolves: #1512620

* Tue Nov 14 2017 Richard Hughes <richard@hughsie.com> 1.0.1-2
- Enable Synaptics MST hub updates.
- Resolves: #1420913

* Thu Nov 09 2017 Richard Hughes <richard@hughsie.com> 1.0.1-1
- Rebase to 1.0.1, specifically the wip/hughsie/rhel75 branch which adds
  back the automake build system and lowers the required versions of deps.
- This also un-neuters fwupd so that most of the plugins are functional,
  for instance allowing updates of Thunderbolt controllers and Logitech
  Unifying devices. However, the LVFS is still disabled.
- Resolves: #1313086

* Mon May 08 2017 Richard Hughes <richard@hughsie.com> 0.8.2-2
- Do not use the LVFS by default.
- Resolves: #1380827

* Thu Apr 20 2017 Richard Hughes <richard@hughsie.com> 0.8.2-1
- Initial upload for RHEL.
- Resolves: #1380827
