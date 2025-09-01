hbar = 1.05457e-34;          % J*s
epsilon_0 = 8.85419e-12;     % F/m
omega_p1 = 2*pi*1.93666e14;       % rad/s
omega_s  = 2*pi*1.93466e14;       % rad/s
omega_p2 = 2*pi*1.93266e14;       % rad/s
L = 3.60026e-4;              % m
v_p1 = 7.18927e7;            % m/s
v_p2 = v_p1;                 % m/s
v_s  = v_p1;                 % m/s
chi3 = 1.9e-19;              % m^2/V^2
A_eff = 1.88e-13;            % m^2
n_s = 2.42;                  % --
n_p1 = n_s;                  % --
n_p2 = n_s;                  % --
n_g = 4.17;                  % --
c = 299792458;               % m/s

i = 3;

sigma_s = [0.9645, 0.9745, 0.9795, 0.9845, 0.9945]
gamma_s = sqrt(2*(1-sigma_s)*v_s^2/L)
Gamma_s = (1-sigma_s)*v_s/L

sigma_sph = sigma_s(3);     % 0.9795
gamma_sph = gamma_s(3);     % 7.6720e+08
Gamma_sph = Gamma_s(3);     % 4.0936e+09

Gamma_sbar = Gamma_s + Gamma_sph;

Lambda_3 = (3*hbar*omega_s^2*v_s^2*chi3)./(n_s^2*epsilon_0*c^2*L*A_eff);    % 1455.4


c_p1_th = sqrt(Gamma_sbar(i)./2/Lambda_3);    % 1.6771e+03
P_p1_th = (hbar*omega_p1*Gamma_sbar(i).^2*Gamma_sbar(i))./(4*Gamma_s(i)*Lambda_3); % 0.003

% %plot 1
% delta_s = 0;
% c_p1 = (0:c_p1_th/100:c_p1_th-c_p1_th/100);
% c_p2 = (0:c_p1_th/100:c_p1_th-c_p1_th/100);
% phi = -pi;
% % parametric_gain = abs(1./(1-1j*(Lambda_3.*c_p1.*c_p2*exp(1j*phi))./(Gamma_sbar(i)-1j*delta_s ))).^2;
% parametric_gain = abs(1./(1-(2*Lambda_3.*c_p1.*c_p2*exp(1j*phi))./(Gamma_sbar(i)-1j*delta_s ))).^2;
% plot(c_p1, 10*log10(parametric_gain));
% hold on;

% % plot 2;
% delta_s = (-50:0.01:50)*1e9;
% c_p1 = 0.5*c_p1_th;
% c_p2 = 0.5*c_p1_th;
% phi = -0;
% % parametric_gain = abs(1./(1-1j*(Lambda_3.*c_p1.*c_p2*exp(1j*phi))./(Gamma_sbar(i)-1j*delta_s ))).^2;
% parametric_gain = abs(1./(1-(2*Lambda_3.*c_p1.*c_p2*exp(1j*phi))./(Gamma_sbar(i)-1j*delta_s ))).^2;
% plot(delta_s*1e-9, 10*log10(parametric_gain));
% hold on;

omega_sb = 0:10e6:Gamma_sbar(i);
Vx = 1 - (4*Gamma_s(i)*Lambda_3*c_p1_th*c_p1_th)./((Gamma_sbar(i) + Lambda_3*c_p1_th*c_p1_th).^2+omega_sb.^2);
Vp = 1 + (4*Gamma_s(i)*Lambda_3*c_p1_th*c_p1_th)./((Gamma_sbar(i) - Lambda_3*c_p1_th*c_p1_th).^2+omega_sb.^2);
plot(omega_sb*1e-9, 10*log10(Vx));
hold on;
plot(omega_sb*1e-9, 10*log10(Vp));

% omega_sb = 0;
% c_p1 = (0:c_p1_th/100:c_p1_th-c_p1_th/100);
% c_p2 = (0:c_p1_th/100:c_p1_th-c_p1_th/100);
% Vx = 1 - (4*Gamma_s(i)*Lambda_3.*c_p1.*c_p2)./((Gamma_sbar(i) + Lambda_3*c_p1_th*c_p1_th).^2+omega_sb.^2);
% Vp = 1 + (4*Gamma_s(i)*Lambda_3.*c_p1.*c_p2)./((Gamma_sbar(i) - Lambda_3*c_p1_th*c_p1_th).^2+omega_sb.^2);
% plot(c_p1, 10*log10(Vx));
% hold on;
% plot(c_p1, 10*log10(Vp));