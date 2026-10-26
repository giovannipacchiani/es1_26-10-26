"""
Mock di button.py — stessa interfaccia pubblica di SwitchButton.

IMPORTANTE: EGG_Line4.py accede direttamente a `button_x.button.is_pressed`
(l'oggetto gpiozero.Button interno), non solo al metodo is_pressed()
esposto da SwitchButton. Questo mock espone un sotto-oggetto `.button`
con lo stesso attributo, per compatibilità totale senza toccare lo
script originale.

Sul robot reale pin=25 (default) è il microswitch paraurti, pin=17 è il
pulsante manuale che l'operatore preme quando il robot raggiunge l'area
di soccorso. In simulazione:
  - pin 25 -> premuto quando lo chassis tocca fisicamente un ostacolo 3D
    (contatti PyBullet reali, vedi SimWorld.obstacle_bumper_pressed)
  - pin 17 -> premuto tenendo il tasto 'r' nella finestra PyBullet (solo
    in modalità GUI; in DIRECT resta sempre False)
"""

from sim_link import get_world


class _ButtonPin:
    """Sostituto minimale di gpiozero.Button: espone solo ciò che
    EGG_Line4.py usa davvero, cioè `.is_pressed`."""

    def __init__(self, source_fn):
        self._source_fn = source_fn

    @property
    def is_pressed(self):
        return bool(self._source_fn())


class SwitchButton:
    def __init__(self, pin=25):
        self.pin = pin
        self.world = get_world()
        source = self.world.rescue_button_pressed if pin == 17 else self.world.obstacle_bumper_pressed
        self.button = _ButtonPin(source)
        self._on_press = None
        self._on_release = None
        self._was_pressed = False

    def is_pressed(self):
        """Ritorna True se il pulsante è attualmente premuto (equivalente
        a `.button.is_pressed`, usato anche da EGG_Line4.py)."""
        return self.button.is_pressed

    def set_callbacks(self, on_press_func=None, on_release_func=None):
        self._on_press = on_press_func
        self._on_release = on_release_func

    def poll_callbacks(self):
        """EGG_Line4.py non la chiama (legge .button.is_pressed nel
        proprio ciclo principale), ma è qui per chi usa i callback come
        sull'hardware reale: va richiamata periodicamente."""
        pressed = self.button.is_pressed
        if pressed and not self._was_pressed and self._on_press:
            self._on_press()
        if not pressed and self._was_pressed and self._on_release:
            self._on_release()
        self._was_pressed = pressed

    def close(self):
        pass


if __name__ == "__main__":
    print("Mock di button.py: va eseguito solo tramite run_simulation.py (richiede un mondo simulato attivo).")
